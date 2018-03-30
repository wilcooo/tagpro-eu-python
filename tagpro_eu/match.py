from collections import namedtuple
import datetime
import heapq

from tagpro_eu.blob import Blob
from tagpro_eu.constants import Team
from tagpro_eu.data import JsonObject
from tagpro_eu.data import ListOf
from tagpro_eu.map import Map
from tagpro_eu.player import Player
from tagpro_eu.player import PlayerEventHandler
from tagpro_eu.player import PlayerEventLogger
from tagpro_eu.player import PlayerStats
from tagpro_eu.util import Time


class Splat(namedtuple('Splat', ['time', 'x', 'y', 'player', 'team'])):
    __slots__ = ()

    def __lt__(self, other):
        return self.time < other.time


class MatchTeam(JsonObject):
    """
    Represent a team object in tagpro.eu match files.
    The exact format can be found on https://tagpro.eu/?science
    """
    __fields__ = {
        'name': str,
        'score': int,
        '__splats__': Blob.from_b64
    }

    def __init__(self, data, strict=False):
        super().__init__(data, strict=strict)

        self.__splatlist__ = None
        self.__stats__ = None

    @property
    def players(self):
        """
        Return a list of players on this team.
        """
        return list(filter(lambda p: p.team == self, self.__parent__.players))

    @property
    def team(self):
        """
        Return the Team value (from tagpro_eu.constants) for this team.
        """
        return Team(self.index + 1)

    @property
    def splats(self):
        """
        Return a list of splats on the map for this team. This is lazy-loaded
        from the __splats__ blob.

        :returns: list of splats
        """
        if self.__splatlist__ is None:
            self._parse_splats()

        return self.__splatlist__

    @property
    def stats(self):
        """
        Return a PlayerStats object containing the aggregate of all this team's
        player's stats.

        TODO: handle team switches properly
        """
        if self.__stats__ is None:
            self.__stats__ = PlayerStats()
            for player in self.players:
                s = PlayerStats()
                player.parse_events(s)
                self.__stats__ += s
        return self.__stats__

    def _parse_splats(self):
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

        # Determine the players who the splats belong to
        player_splats = []

        class PlayerSplat(namedtuple('PlayerSplat', ['time', 'player'])):
            __slots__ = ()

            def __lt__(self, other):
                return self.time < other.time

        class PlayerSplatsHandler(PlayerEventHandler):
            def __init__(self, player, team):
                self.player = player
                self.team = team

            def drop(self, time, old_flag, powers, team):
                self.pop(time, powers, team)

            def pop(self, time, powers, team):
                if team == self.team:
                    heapq.heappush(player_splats,
                                   PlayerSplat(time, self.player))

        for p in self.__parent__.players:
            h = PlayerSplatsHandler(p, self.team)
            p.parse_events(h)

        blob = self.__splats__
        blob.reset()

        self.__splatlist__ = []

        x = bits(self.__parent__.map.width)
        y = bits(self.__parent__.map.height)

        index = 0

        while not blob.end():
            n = blob.read_tally()

            if n > 0:
                for i in range(n):
                    ps = heapq.heappop(player_splats)
                    self.__splatlist__.append(
                        Splat(ps.time,
                              blob.read_fixed(x[0]) - x[1],
                              blob.read_fixed(y[0]) - y[1],
                              ps.player,
                              self))

            index += 1

    def __eq__(self, other):
        """
        I don't see a reason to compare teams across matches, so comparing
        parents is fine.
        """
        if isinstance(other, Team):
            return self.team == other

        return other is not None and self.index == other.index and\
            self.__parent__ == other.__parent__

    def __repr__(self):
        return f'MatchTeam(name={self.name!r})'


class Match(JsonObject):
    """
    Represents a match object in tagpro.eu match files.
    The exact format can be found on https://tagpro.eu/?science
    """
    __fields__ = {
        'server': str,               # Domain name of the game server
        'port': int,
        'official': bool,            # Played on an "official" server
        'group': str,                # Group ID
        # Start of the match
        'date': datetime.datetime.fromtimestamp,
        'timeLimit': int,            # In minutes
        'duration': Time,            # In frames
        'finished': bool,
        'map': Map,                  # Map object
        'players': ListOf(Player),   # Array of player objects
        'teams': ListOf(MatchTeam),  # Array of team objects
    }

    def __init__(self, data, strict=False):
        super().__init__(data, strict=strict)

        self.__splats__ = None

    def team(self, team):
        """
        Return the MatchTeam object corresponding to the given Team enum value.

        :param team: the team index (from tagpro_eu.constants.Team)
        :returns: the MatchTeam object
        """
        if team == Team.red:
            return self.teams[0]
        elif team == Team.blue:
            return self.teams[1]
        else:
            return None

    @property
    def team_red(self):
        """
        Return the red team.
        """
        return self.team(Team.red)

    @property
    def team_blue(self):
        """
        Return the blue team.
        """
        return self.team(Team.blue)

    @property
    def splats(self):
        """
        Return a list of all splats in the game.
        """
        if self.__splats__ is None:
            sr = self.team_red.splats
            sb = self.team_blue.splats
            self.__splats__ = []

            ir, ib = 0, 0

            while ir < len(sr) or ib < len(sb):
                if ib == len(sb) or ir < len(sr) and sr[ir] < sb[ib]:
                    self.__splats__.append(sr[ir])
                    ir += 1
                else:
                    self.__splats__.append(sb[ib])
                    ib += 1

        return self.__splats__

    def __eq__(self, other):
        return self.server == other.server and\
               self.port == other.port and\
               self.date == other.date

    def __compute_cap_diff__(self):
        """
        Compute the caps_from and caps_against for all players in the game.
        """
        Cap = namedtuple('Cap', ['time', 'team'])
        caps = []

        class CapAggregator(PlayerEventHandler):
            def capture(self, time, _, __, team):
                caps.append(Cap(time, team))

        agg = CapAggregator()

        for player in self.players:
            player.parse_events(agg)

        caps.sort()

        class CapDiffHandler(PlayerEventHandler):
            def __init__(self, caplist, player):
                self.team = Team.none
                self.player = player
                self.caplist = caplist
                self.index = 0

            def catch_up(self, time):
                while self.index < len(self.caplist)\
                        and self.caplist[self.index].time <= time:
                    if self.team != Team.none:
                        capteam = self.caplist[self.index].team
                        if capteam == self.team:
                            self.player.__caps_for__ += 1
                        else:
                            self.player.__caps_against__ += 1
                    self.index += 1

            def join(self, time, team):
                self.catch_up(time)
                self.team = team

            def quit(self, time, _, __, ___):
                self.catch_up(time)
                self.team = Team.none

            def switch(self, time, _, __, team):
                self.catch_up(time)
                self.team = team

            def end(self, time, _, __, team):
                self.catch_up(time)
                self.team = Team.none

        for player in self.players:
            player.__caps_for__ = 0
            player.__caps_against__ = 0
            player.parse_events(CapDiffHandler(caps, player))

    def create_timeline(self, sort=False):
        """
        Return a timeline of events for all players in the match. Each event
        is a tuple of the time, the event (as a string) and the corresponding
        Player object.

        If sort is set to False (default), the timeline will be returned as a
        priority queue (MinHeap). The minimum (that is, occurred first) value
        can be obtained by repeatedly calling heappop from the module heapq.
        Using a priority queue increases performance for creating the timeline.
        If sort is set to True, the timeline is automatically sorted and you
        don't have to bother using heapq.

        :param sort: whether or not to sort the timeline
        :returns: the match timeline
        """
        heap = []

        for player in self.players:
            handler = PlayerEventLogger(heap, player)
            player.parse_events(handler)

        if sort:
            return sorted(heap)
        return heap

    def print_timeline(self):
        """
        Format and print the timeline generated by create_timeline.
        """
        timeline = self.create_timeline()

        while timeline:
            time, event, player = heapq.heappop(timeline)
            print(f'{time} | {player.name:<12} | {event}')

    def __repr__(self):
        return f'Match(server={self.server!r}, port={self.port!r})'

    def print_scoreboard(self, sort_key=None, fields=None):
        """
        Format and print a scoreboard for the match. If desired, a custom
        sorting key and list of fields to show can be given. By default, the
        players will be sorted by their score in descending order, and all
        fields will be shown.

        In fields, every field should be given as a string. The possible fields
        are every attribute of PlayerStats, plus name and score.

        :param sort_key: function that returns the sorting key for a player
        :param fields: the list of fields (as strings) to show
        """
        def default_sort(p):
            return -p.score

        non_stat_attrs = ('name', 'score', 'points')

        def format_field(p, field):
            if field in non_stat_attrs:
                v = getattr(p, field)
            else:
                v = getattr(p.stats, field)

            return str(v).center(field_width(field))

        def field_name(field):
            return 'Powerups' if field == 'pups_total' else field.title()

        def field_width(field):
            return 12 if field == 'name' else 8

        if sort_key is None:
            sort_key = default_sort

        if fields is None:
            fields = ['name', 'score', 'time', 'tags', 'pops', 'grabs',
                      'drops', 'hold', 'captures', 'returns', 'prevent',
                      'button', 'block', 'pups_total', 'points']

        line = '+' + '+'.join('-' * field_width(f) for f in fields) + '+'
        print(line)
        print('|' + '|'.join(field_name(f).center(field_width(f))
                             for f in fields) + '|')
        print(line)

        for p in sorted(self.players, key=sort_key):
            print('|' + '|'.join(format_field(p, f) for f in fields) + '|')

        print(line)
