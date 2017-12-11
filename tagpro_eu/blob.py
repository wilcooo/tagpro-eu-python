import base64

from tagpro_eu import constants
from tagpro_eu.handlers.player import PlayerEventHandler
from tagpro_eu.handlers.map import MapHandler


class Blob:
    def __init__(self, data):
        self.data = base64.b64decode(data)
        self.pos = 0

    def end(self):
        return self.pos >> 3 >= len(self.data)

    def read_bool(self):
        res = 0
        if not self.end():
            res = self.data[self.pos >> 3] >> 7 - (self.pos & 7) & 1
        self.pos += 1
        return res

    def read_fixed(self, bits):
        res = 0
        for _ in range(bits):
            res = res << 1 | self.read_bool()
        return res

    def read_tally(self):
        res = 0
        while self.read_bool():
            res += 1
        return res

    def read_footer(self):
        size = self.read_fixed(2) << 3
        free = 8 - (self.pos & 7) & 7
        size |= free
        minimum = 0

        while free < size:
            minimum += 1 << free
            free += 8

        return self.read_fixed(size) + minimum

    def reset(self):
        self.pos = 0


def player_events(blob, team, duration, handler=None):
    if handler is None:
        handler = PlayerEventHandler()

    time = 0
    flag = constants.NO_FLAG
    powers = constants.NO_POWER
    prevent = False
    button = False
    block = False

    if team:
        handler.join(time, team)

    while not blob.end():
        new_team = team
        if blob.read_bool():
            if team == constants.NO_TEAM:
                new_team = 1 + blob.read_bool()
            elif blob.read_bool():
                new_team = constants.NO_TEAM
            elif team == constants.RED_TEAM:
                new_team = constants.BLUE_TEAM
            elif team == constants.BLUE_TEAM:
                new_team = constants.RED_TEAM

        drop_pop = blob.read_bool()
        returns = blob.read_tally()
        tags = blob.read_tally()
        grab = not flag and blob.read_bool()
        captures = blob.read_tally()

        # wtf
        keep = not drop_pop and new_team and \
            (new_team == team or not team) and \
            (not captures or not flag and
             not grab or blob.read_bool())

        new_flag = flag
        if grab:
            if keep:
                new_flag = 1 + blob.read_fixed(2)
            else:
                new_flag = constants.TEMP_FLAG

        powerups = blob.read_tally()
        pdown = constants.NO_POWER
        pup = constants.NO_POWER

        for p in constants.POWERUPS:
            if powers & p and blob.read_bool():
                pdown |= p
            elif powerups and blob.read_bool():
                pup |= p
                powerups -= 1

        toggle_prevent = blob.read_bool()
        toggle_button = blob.read_bool()
        toggle_block = blob.read_bool()

        time += 1 + blob.read_footer()

        if not team and new_team:
            team = new_team
            handler.join(time, team)

        for i in range(returns):
            handler.return_(time, flag, powers, team)

        for i in range(tags):
            handler.tag(time, flag, powers, team)

        if grab:
            flag = new_flag
            handler.grab(time, flag, powers, team)

        for i in range(captures):
            if keep or not flag:
                handler.flagless_capture(time, flag, powers, team)
            else:
                handler.capture(time, flag, powers, team)
                flag = constants.NO_FLAG
                keep = True

        for p in constants.POWERUPS:
            if pdown & p:
                powers ^= p
                handler.powerdown(time, flag, p, powers, team)
            elif pup & p:
                powers |= p
                handler.powerup(time, flag, p, powers, team)

        for i in range(powerups):
            handler.duplicate_powerup(time, flag, powers, team)

        if toggle_prevent:
            if prevent:
                handler.stop_prevent(time, flag, powers, team)
                prevent = False
            else:
                handler.start_prevent(time, flag, powers, team)
                prevent = True

        if toggle_button:
            if button:
                handler.stop_button(time, flag, powers, team)
                button = False
            else:
                handler.start_button(time, flag, powers, team)
                button = True

        if toggle_block:
            if block:
                handler.stop_block(time, flag, powers, team)
                block = False
            else:
                handler.start_block(time, flag, powers, team)
                block = True

        if drop_pop:
            if flag:
                handler.drop(time, flag, powers, team)
                flag = constants.NO_FLAG
            else:
                handler.pop(time, powers, team)

        if new_team != team:
            if not new_team:
                handler.quit(time, flag, powers, team)
                powers = constants.NO_POWER
            else:
                handler.switch(time, flag, powers, new_team)

            flag = constants.NO_FLAG
            team = new_team

    handler.end(duration, flag, powers, team)


def parse_map(blob, width, handler=None):
    if handler is None:
        handler = MapHandler()

    x, y = 0, 0

    while not blob.end() or x > 0:
        tile = blob.read_fixed(6)
        if tile != constants.EMPTY_TILE:
            # idk
            if tile < 6:
                tile += 9
            elif tile < 13:
                tile = (tile - 4) * 10
            elif tile < 17:
                tile += 77
            elif tile < 20:
                tile = (tile - 7) * 10
            elif tile < 22:
                tile += 110
            else:
                tile = (tile - 8) * 10

        for i in range(blob.read_footer() + 1):
            if x == 0:
                handler.height(y)
            handler.tile(x, y, tile)

            x += 1
            if x == width:
                x = 0
                y += 1
