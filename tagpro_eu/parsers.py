from tagpro_eu.constants import Flag, Powerup, Team, Tile
from tagpro_eu.handlers.player import PlayerEventHandler
from tagpro_eu.handlers.map import MapHandler
from tagpro_eu.handlers.splats import SplatsHandler


def parse_player(blob, team, duration, handler=None):
    if handler is None:
        handler = PlayerEventHandler()

    blob.reset()

    time = 0
    flag = Flag.none
    powers = Powerup.none
    prevent = False
    button = False
    block = False

    if team:
        handler.join(time, team)

    while not blob.end():
        new_team = team
        if blob.read_bool():
            if team == Team.none:
                new_team = Team(1 + blob.read_bool())
            elif blob.read_bool():
                new_team = Team.none
            elif team == Team.red:
                new_team = Team.blue
            elif team == Team.blue:
                new_team = Team.red

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
                new_flag = Flag(1 + blob.read_fixed(2))
            else:
                new_flag = Flag.temp

        powerups = blob.read_tally()
        pdown = Powerup.none
        pup = Powerup.none

        for p in Powerup.enumerate():
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
                flag = Flag.none
                keep = True

        for p in Powerup.enumerate():
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
                flag = Flag.none
            else:
                handler.pop(time, powers, team)

        if new_team != team:
            if not new_team:
                handler.quit(time, flag, powers, team)
                powers = Powerup.none
            else:
                handler.switch(time, flag, powers, new_team)

            flag = Flag.none
            team = new_team

    handler.end(duration, flag, powers, team)


def parse_map(blob, width, handler=None):
    if handler is None:
        handler = MapHandler()

    blob.reset()

    x, y = 0, 0

    while not blob.end() or x > 0:
        tile = blob.read_fixed(6)
        if tile != Tile.empty:
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


def parse_splats(blob, width, height, handler=None):
    def bits(size):
        size *= 40
        grid = size - 1
        result = 32
        if not (grid & 0xFFFF0000):
            result -= 16
            grid <<= 16
        if not (grid & 0xFF000000):
            result -= 8
            grid <<= 8
        if not (grid & 0xF0000000):
            result -= 4
            grid <<= 4
        if not (grid & 0xC0000000):
            result -= 2
            grid <<= 2
        if not (grid & 0x80000000):
            result -= 1

        return (result, ((1 << result) - size >> 1) + 20)

    if handler is None:
        handler = SplatsHandler()

    blob.reset()

    x = bits(width)
    y = bits(height)

    index = 0

    while not blob.end():
        n = blob.read_tally()

        if n > 0:
            splats = []
            for i in range(n):
                splats.append((blob.read_fixed(x[0]) - x[1],
                               blob.read_fixed(y[0]) - y[1]))
            handler.splats(splats, index)

        index += 1
