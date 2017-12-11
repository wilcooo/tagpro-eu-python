import constants


class PlayerEventHandler:
    # flake8: noqa
    def join(self, time, new_team): pass
    def quit(self, time, old_flag, old_powers, old_team): pass
    def switch(self, time, old_flag, powers, new_team): pass
    def grab(self, time, new_flag, powers, team): pass
    def capture(self, time, old_flag, powers, team): pass
    def flagless_capture(self, time, flag, powers, team): pass
    def powerup(self, time, flag, power_up, new_powers, team): pass
    def duplicate_powerup(self, time, flag, powers, team): pass
    def powerdown(self, time, flag, power_down, new_powers, team): pass
    def return_(self, time, flag, powers, team): pass
    def tag(self, time, old_flag, powers, team): pass
    def drop(self, time, old_flag, powers, team): pass
    def pop(self, time, powers, team): pass
    def start_prevent(self, time, flag, powers, team): pass
    def stop_prevent(self, time, flag, powers, team): pass
    def start_button(self, time, flag, powers, team): pass
    def stop_button(self, time, flag, powers, team): pass
    def start_block(self, time, flag, powers, team): pass
    def stop_block(self, time, flag, powers, team): pass
    def end(self, time, flag, powers, team): pass


class PlayerStatCounter(PlayerEventHandler):
    def __init__(self):
        self.tags = 0
        self.pops = 0
        self.grabs = 0
        self.drops = 0
        self.hold = 0
        self.captures = 0
        self.returns = 0
        self.prevent = 0
        self.button = 0
        self.block = 0
        self.pups = {
            constants.NO_POWER: 0, # unknown

            constants.JUKE_JUICE: 0,
            constants.ROLLING_BOMB: 0,
            constants.TAGPRO: 0,
            constants.TOP_SPEED: 0,
        }
        self.pup_time = {
            constants.JUKE_JUICE: 0,
            constants.ROLLING_BOMB: 0,
            constants.TAGPRO: 0,
            constants.TOP_SPEED: 0,
        }
        self.time = 0

        self.ingame_since = -1
        self.hold_since = -1
        self.prevent_since = -1
        self.button_since = -1
        self.block_since = -1
        self.pup_since = {
            constants.JUKE_JUICE: -1,
            constants.ROLLING_BOMB: -1,
            constants.TAGPRO: -1,
            constants.TOP_SPEED: -1,
        }

    def join(self, time, new_team):
        self.ingame_since = time

    def quit(self, time, old_flag, old_powers, old_team):
        if self.ingame_since >= 0:
            self.time += time - self.ingame_since
            self.ingame_since = -1

    def switch(self, time, old_flag, powers, new_team): pass

    def grab(self, time, new_flag, powers, team):
        self.grabs += 1
        self.hold_since = time

    def capture(self, time, old_flag, powers, team):
        self.captures += 1

        if self.hold_since >= 0:
            self.hold += time - self.hold_since
            self.hold_since = -1

    def flagless_capture(self, time, flag, powers, team):
        self.captures += 1

    def powerup(self, time, flag, power_up, new_powers, team):
        self.pups[power_up] += 1
        self.pup_since[power_up] = time

    def duplicate_powerup(self, time, flag, powers, team):
        self.pups[constants.NO_POWER] += 1

    def powerdown(self, time, flag, power_down, new_powers, team):
        if self.pup_since[power_down] >= 0:
            self.pup_time[power_down] += time - self.pup_since[power_down]
            self.pup_since[power_down] = -1

    def return_(self, time, flag, powers, team):
        self.returns += 1
        self.tags += 1

    def tag(self, time, flag, powers, team):
        self.tags += 1

    def drop(self, time, old_flag, powers, team):
        self.pops += 1
        self.drops += 1

        if self.hold_since >= 0:
            self.hold += time - self.hold_since
            self.hold_since = -1

    def pop(self, time, powers, team):
        self.pops += 1

    def start_prevent(self, time, flag, powers, team):
        self.prevent_since = time

    def stop_prevent(self, time, flag, powers, team):
        if self.prevent_since >= 0:
            self.prevent += time - self.prevent_since
            self.prevent_since = -1

    def start_button(self, time, flag, powers, team):
        self.button_since = time

    def stop_button(self, time, flag, powers, team):
        if self.button_since >= 0:
            self.button += time - self.button_since
            self.button_since = -1

    def start_block(self, time, flag, powers, team):
        self.block_since = time

    def stop_block(self, time, flag, powers, team):
        if self.block_since >= 0:
            self.block += time - self.block_since
            self.block_since = -1

    def end(self, time, flag, powers, team):
        if self.ingame_since >= 0:
            self.time += time - self.ingame_since
            self.ingame_since = -1

        for p in constants.POWERUPS:
            if self.pup_since[p] >= 0:
                self.pup_time[p] += time - self.pup_since[p]
                self.pup_since[p] = -1

        if self.hold_since >= 0:
            self.hold += time - self.hold_since
            self.hold_since = -1

        if self.prevent_since >= 0:
            self.prevent += time - self.prevent_since
            self.prevent_since = -1

        if self.button_since >= 0:
            self.button += time - self.button_since
            self.button_since = -1

        if self.block_since >= 0:
            self.block += time - self.block_since
            self.block_since = -1


class PlayerEventLogger:
    @staticmethod
    def log(time, msg):
        time //= 60
        m, s = divmod(time, 60)

        print(f'{m:0>2}:{s:0>2} | {msg}')

    def join(self, time, new_team):
        PlayerEventLogger.log(time, f'Join team {new_team}')
        
    def quit(self, time, old_flag, old_powers, old_team):
        PlayerEventLogger.log(time, f'Leave team {old_team} with flag {old_flag} and '
                  f'powers {old_powers}')

    def switch(self, time, old_flag, powers, new_team):
        PlayerEventLogger.log(time, f'Switch to team {new_team} with flag {old_flag} and '
                  f'powers {powers}')

    def grab(self, time, new_flag, powers, team):
        PlayerEventLogger.log(time, f'Grab flag {new_flag}')

    def capture(self, time, old_flag, powers, team):
        PlayerEventLogger.log(time, f'Capture flag {old_flag}')

    def flagless_capture(self, time, flag, powers, team):
        PlayerEventLogger.log(time, 'Capture marsball')

    def powerup(self, time, flag, power_up, new_powers, team):
        PlayerEventLogger.log(time, f'Power up {power_up}')

    def duplicate_powerup(self, time, flag, powers, team):
        PlayerEventLogger.log(time, f'Grab duplicate powerup')

    def powerdown(self, time, flag, power_down, new_powers, team):
        PlayerEventLogger.log(time, f'Power down {power_down}')

    def return_(self, time, flag, powers, team):
        PlayerEventLogger.log(time, 'Return')

    def tag(self, time, old_flag, powers, team):
        PlayerEventLogger.log(time, 'Tag')

    def drop(self, time, old_flag, powers, team):
        PlayerEventLogger.log(time, 'Drop')

    def pop(self, time, powers, team):
        PlayerEventLogger.log(time, 'Pop')

    def start_prevent(self, time, flag, powers, team):
        PlayerEventLogger.log(time, 'Start preventing')

    def stop_prevent(self, time, flag, powers, team):
        PlayerEventLogger.log(time, 'Stop preventing')

    def start_button(self, time, flag, powers, team):
        PlayerEventLogger.log(time, 'Start buttoning')

    def stop_button(self, time, flag, powers, team):
        PlayerEventLogger.log(time, 'Stop buttoning')

    def start_block(self, time, flag, powers, team):
        PlayerEventLogger.log(time, 'Start blocking')

    def stop_block(self, time, flag, powers, team):
        PlayerEventLogger.log(time, 'Stop blocking')

    def end(self, time, flag, powers, team):
        PlayerEventLogger.log(time, 'Game ends')
