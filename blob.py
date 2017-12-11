import base64

import constants
from handlers import PlayerEventHandler


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


class PlayerEvents(Blob):
    def __init__(self, data, team, duration, handler=None):
        super(PlayerEvents, self).__init__(data)

        if handler is None:
            handler = PlayerEventHandler()

        time = 0
        flag = constants.NO_FLAG
        powers = constants.NO_POWER
        prevent = False
        button = False
        block = False

        while not self.end():
            new_team = team
            if self.read_bool():
                if team == constants.NO_TEAM:
                    new_team = 1 + self.read_bool()
                elif self.read_bool():
                    new_team = constants.NO_TEAM
                elif team == constants.RED_TEAM:
                    new_team = constants.BLUE_TEAM
                elif team == constants.BLUE_TEAM:
                    new_team = constants.RED_TEAM

            drop_pop = self.read_bool()
            returns = self.read_tally()
            tags = self.read_tally()
            grab = not flag and self.read_bool()
            captures = self.read_tally()

            # wtf
            keep = not drop_pop and new_team and \
                (new_team == team or not team) and \
                (not captures or not flag and
                 not grab or self.read_bool())

            new_flag = flag
            if grab:
                if keep:
                    new_flag = 1 + self.read_fixed(2)
                else:
                    new_flag = constants.TEMP_FLAG

            powerups = self.read_tally()
            pdown = constants.NO_POWER
            pup = constants.NO_POWER

            for p in constants.POWERUPS:
                if powers & p:
                    if self.read_bool():
                        pdown |= p
                elif powerups and self.read_bool():
                    pup |= p
                    powerups -= 1

            toggle_prevent = self.read_bool()
            toggle_button = self.read_bool()
            toggle_block = self.read_bool()

            time += 1 + self.read_footer()

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
