import heapq

from collections import defaultdict
from tagpro_eu.constants import Powerup


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
    def tag(self, time, flag, powers, team): pass
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
        self.pups = defaultdict(int)
        self.pup_time = defaultdict(int)
        self.time = 0

        self.ingame_since = -1
        self.hold_since = -1
        self.prevent_since = -1
        self.button_since = -1
        self.block_since = -1
        self.pup_since = defaultdict(lambda: -1)

    @property
    def pups_total(self):
        return sum(self.pups.values())

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
        self.pups[Powerup.none] += 1

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

        for p in Powerup.enumerate():
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


class PlayerEventLogger(PlayerEventHandler):
    def __init__(self, heap=None, player=None):
        if heap is None:
            heap = []

        self.heap = heap
        self.player = player

    def get_team_name(self, team):
        if self.player is None:
            return str(team)

        return self.player.__parent__.teams[team - 1].name

    def join(self, time, new_team):
        heapq.heappush(self.heap,
            (time, f'Join team {self.get_team_name(new_team)}', self.player))
        
    def quit(self, time, old_flag, old_powers, old_team):
        heapq.heappush(self.heap,
            (time, f'Leave team {self.get_team_name(old_team)}', self.player))

    def switch(self, time, old_flag, powers, new_team):
        heapq.heappush(self.heap,
            (time, f'Switch to team {self.get_team_name(new_team)}',
             self.player))

    def grab(self, time, new_flag, powers, team):
        heapq.heappush(self.heap,
            (time, f'Grab {new_flag!s}', self.player))

    def capture(self, time, old_flag, powers, team):
        heapq.heappush(self.heap,
            (time, f'Capture {old_flag!s}', self.player))

    def flagless_capture(self, time, flag, powers, team):
        heapq.heappush(self.heap,
            (time, 'Capture marsball', self.player))

    def powerup(self, time, flag, power_up, new_powers, team):
        heapq.heappush(self.heap,
            (time, f'Power up {power_up!s}', self.player))

    def duplicate_powerup(self, time, flag, powers, team):
        heapq.heappush(self.heap,
            (time, f'Grab duplicate powerup', self.player))

    def powerdown(self, time, flag, power_down, new_powers, team):
        heapq.heappush(self.heap,
            (time, f'Power down {power_down!s}', self.player))

    def return_(self, time, flag, powers, team):
        heapq.heappush(self.heap, (time, 'Return', self.player))

    def tag(self, time, flag, powers, team):
        heapq.heappush(self.heap, (time, 'Tag', self.player))

    def drop(self, time, old_flag, powers, team):
        heapq.heappush(self.heap,
            (time, f'Drop {old_flag!s}', self.player))

    def pop(self, time, powers, team):
        heapq.heappush(self.heap, (time, 'Pop', self.player))

    def start_prevent(self, time, flag, powers, team):
        heapq.heappush(self.heap, (time, 'Start preventing', self.player))

    def stop_prevent(self, time, flag, powers, team):
        heapq.heappush(self.heap, (time, 'Stop preventing', self.player))

    def start_button(self, time, flag, powers, team):
        heapq.heappush(self.heap, (time, 'Start buttoning', self.player))

    def stop_button(self, time, flag, powers, team):
        heapq.heappush(self.heap, (time, 'Stop buttoning', self.player))

    def start_block(self, time, flag, powers, team):
        heapq.heappush(self.heap, (time, 'Start blocking', self.player))

    def stop_block(self, time, flag, powers, team):
        heapq.heappush(self.heap, (time, 'Stop blocking', self.player))

    def end(self, time, flag, powers, team):
        heapq.heappush(self.heap, (time, 'Game ends', self.player))
