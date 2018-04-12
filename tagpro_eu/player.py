from collections import defaultdict
import heapq

from tagpro_eu.blob import Blob
from tagpro_eu.constants import Flag, Flair, Powerup, Team
from tagpro_eu.data import JsonObject
from tagpro_eu.util import Time


class Player(JsonObject):
    """
    Represents a player object in tagpro.eu match files.
    The exact format can be found on https://tagpro.eu/?science
    """
    __fields__ = {
        'auth': bool,
        'name': str,
        'flair': Flair,
        'degree': int,
        'score': int,
        'points': int,    # rank points
        '__team__': int,  # at start of match; 1 = red, 2 = blue, 0 = join late
        'events': Blob.from_b64,
    }

    def __init__(self, data, strict=False):
        super().__init__(data, strict=strict)

        self.__stats__ = None
        self.__caps_for__ = None
        self.__caps_against__ = None

    @property
    def caps_for(self):
        """
        Return the number of captures done by the player's team.
        """
        if self.__caps_for__ is None:
            self.__parent__.__compute_cap_diff__()
        return self.__caps_for__

    @property
    def caps_against(self):
        """
        Return the number of captures done by the player's enemy's team.
        """
        if self.__caps_against__ is None:
            self.__parent__.__compute_cap_diff__()
        return self.__caps_against__

    @property
    def cap_diff(self):
        """
        Return caps_for - caps_against.
        """
        return self.caps_for - self.caps_against

    @property
    def team(self):
        """
        Return the MatchTeam object for the team this player is in.
        """
        return self.__parent__.team(self.__team__)

    @property
    def stats(self):
        """
        Return a PlayerStats object corresponding to the player's stats. This
        is lazy-loaded from the events blob.

        :returns: the PlayerStats object for this player
        """
        if self.__stats__ is None:
            handler = PlayerStats()
            self.parse_events(handler)
            handler.caps_for = self.caps_for
            handler.caps_against = self.caps_against
            self.__stats__ = handler
        return self.__stats__

    def parse_events(self, handler):
        """
        Parse the events blob using the given reader.

        :param handler: the PlayerEventHandler object used to read the events
        """
        team = self.__team__
        duration = self.__parent__.duration

        blob = self.events
        blob.reset()

        time = Time()
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
                if powers & p:  # Short-circuit 'and' will NOT work
                    if blob.read_bool():
                        pdown |= p
                elif powerups:
                    if blob.read_bool():
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

    def __lt__(self, other):
        """
        Necessary for building a heap of events.
        This obviously does not actually work.
        """
        return False

    def __eq__(self, other):
        """
        There's no "safe" way to compare players across matches, as even if a
        player is authorized, their name might have belonged to someone else
        in the past.

        If you analyze public games, I strongly recommend against using == on
        players, and writing your own method instead. For private/competitive
        games, this method should be fine though.
        """
        return other is not None and self.name == other.name

    def __repr__(self):
        return f'Player(name={self.name!r})'


class PlayerEventHandler:
    """
    Event handler for reading a player's events blob.
    """
    def join(self, time, new_team):
        pass

    def quit(self, time, old_flag, old_powers, old_team):
        pass

    def switch(self, time, old_flag, powers, new_team):
        pass

    def grab(self, time, new_flag, powers, team):
        pass

    def capture(self, time, old_flag, powers, team):
        pass

    def flagless_capture(self, time, flag, powers, team):
        pass

    def powerup(self, time, flag, power_up, new_powers, team):
        pass

    def duplicate_powerup(self, time, flag, powers, team):
        pass

    def powerdown(self, time, flag, power_down, new_powers, team):
        pass

    def return_(self, time, flag, powers, team):
        pass

    def tag(self, time, flag, powers, team):
        pass

    def drop(self, time, old_flag, powers, team):
        pass

    def pop(self, time, powers, team):
        pass

    def start_prevent(self, time, flag, powers, team):
        pass

    def stop_prevent(self, time, flag, powers, team):
        pass

    def start_button(self, time, flag, powers, team):
        pass

    def stop_button(self, time, flag, powers, team):
        pass

    def start_block(self, time, flag, powers, team):
        pass

    def stop_block(self, time, flag, powers, team):
        pass

    def end(self, time, flag, powers, team):
        pass


class PlayerStats(PlayerEventHandler):
    """
    Implementation of PlayerEventHandler that accumulates the player's stats.
    """
    def __init__(self):
        self.tags = 0
        self.pops = 0
        self.grabs = 0
        self.drops = 0
        self.hold = Time()
        self.captures = 0
        self.returns = 0
        self.prevent = Time()
        self.button = Time()
        self.block = Time()
        self.pups = defaultdict(int)
        self.pup_time = defaultdict(Time)
        self.time = Time()

        self.ingame_since = -1
        self.hold_since = -1
        self.prevent_since = -1
        self.button_since = -1
        self.block_since = -1
        self.pup_since = defaultdict(lambda: -1)

        # these are supplied by the player object
        self.caps_for = self.caps_against = 0

    @property
    def cap_diff(self):
        return self.caps_for - self.caps_against

    @property
    def pups_total(self):
        """
        Return the total number of powerups picked up by the player.

        :returns: number of powerups
        """
        return sum(self.pups.values())

    def __add__(self, other):
        new = PlayerStats()
        keys = ['tags', 'pops', 'grabs', 'drops', 'hold', 'captures',
                'returns', 'prevent', 'button', 'block', 'time',
                'caps_for', 'caps_against']
        pup_dicts = ['pups', 'pup_time']

        for k in keys:
            setattr(new, k, getattr(self, k) + getattr(other, k))

        for k in pup_dicts:
            for s in self, other:
                for p, n in getattr(s, k).items():
                    getattr(new, k)[p] += n

        return new

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
    """
    Implementation of PlayerEventHandler that logs all events to a priority
    queue (MinHeap). Each earliest event can be collected from the queue by
    repeatedly calling heappop from the module heapq.
    """
    def __init__(self, heap=None, player=None):
        """
        Initialize an event logger with the given queue and player object.
        If no queue is given, a new one is made which can be later acquired
        from the heap attribute.

        :param heap: the priority queue to log to
        :param player: the Player object corresponding to this logger
        """
        if heap is None:
            heap = []

        self.heap = heap
        self.player = player

    def get_team_name(self, team):
        """
        Return the name of a team. If a Player object was given in the
        constructor, the actual team name as set in the json object is used.
        Otherwise, the default name (red/blue) is used.

        :param team: the team to get the name of
        :returns: the name of the team
        """
        if self.player is None:
            return str(team)

        return self.player.__parent__.team(team).name

    def join(self, time, new_team):
        heapq.heappush(
            self.heap,
            (time, f'Join team {self.get_team_name(new_team)}', self.player))

    def quit(self, time, old_flag, old_powers, old_team):
        heapq.heappush(
            self.heap,
            (time, f'Leave team {self.get_team_name(old_team)}', self.player))

    def switch(self, time, old_flag, powers, new_team):
        heapq.heappush(
            self.heap,
            (time, f'Switch to team {self.get_team_name(new_team)}',
             self.player))

    def grab(self, time, new_flag, powers, team):
        heapq.heappush(
            self.heap,
            (time, f'Grab {new_flag!s}', self.player))

    def capture(self, time, old_flag, powers, team):
        heapq.heappush(
            self.heap,
            (time, f'Capture {old_flag!s}', self.player))

    def flagless_capture(self, time, flag, powers, team):
        heapq.heappush(
            self.heap,
            (time, 'Capture marsball', self.player))

    def powerup(self, time, flag, power_up, new_powers, team):
        heapq.heappush(
            self.heap,
            (time, f'Power up {power_up!s}', self.player))

    def duplicate_powerup(self, time, flag, powers, team):
        heapq.heappush(
            self.heap,
            (time, f'Grab duplicate powerup', self.player))

    def powerdown(self, time, flag, power_down, new_powers, team):
        heapq.heappush(
            self.heap,
            (time, f'Power down {power_down!s}', self.player))

    def return_(self, time, flag, powers, team):
        heapq.heappush(self.heap, (time, 'Return', self.player))

    def tag(self, time, flag, powers, team):
        heapq.heappush(self.heap, (time, 'Tag', self.player))

    def drop(self, time, old_flag, powers, team):
        heapq.heappush(
            self.heap,
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
