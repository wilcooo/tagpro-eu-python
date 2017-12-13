import datetime
import heapq
import json

from tagpro_eu.blob import Blob
from tagpro_eu.handlers.map import MapSaver
from tagpro_eu.handlers.player import PlayerStatCounter
from tagpro_eu.handlers.player import PlayerEventLogger
from tagpro_eu.handlers.splats import SplatsSaver
from tagpro_eu.parsers import parse_map
from tagpro_eu.parsers import parse_player
from tagpro_eu.parsers import parse_splats
from tagpro_eu.util import format_time


class JsonObject:
    def __init__(self, data, strict=False):
        for f, t in self.__fields__.items():
            try:
                value = data[f.strip('_')]
            except KeyError:
                if strict:
                    raise
                value = None

            if value is not None:
                value = t(value)

            if isinstance(value, JsonObject):
                value.__parent__ = self
            elif isinstance(value, list):
                for item in value:
                    item.__parent__ = self

            setattr(self, f, value)

    @classmethod
    def from_string(cls, s, strict=False):
        return cls(json.loads(s), strict=strict)

    @classmethod
    def from_file(cls, filename, strict=False):
        with open(filename) as f:
            return cls(json.load(f), strict=strict)


class Map(JsonObject):
    __fields__ = {
        'name': str,
        'author': str,
        'type': str,        # ctf, nf, mb etc., empty for unofficial maps
        'marsballs': int,   # number
        'width': int,
        '__tiles__': Blob,
    }

    def __init__(self, data):
        super(Map, self).__init__(data)

        self.__tilemap__ = None

    @property
    def tiles(self):
        if self.__tilemap__ is None:
            self.parse_tiles()

        return self.__tilemap__

    @property
    def height(self):
        if self.__tilemap__ is None:
            self.parse_tiles()

        return len(self.__tilemap__)

    def parse_tiles(self):
        handler = MapSaver()
        parse_map(self.__tiles__, self.width, handler=handler)

        self.__tilemap__ = handler.tiles


class Player(JsonObject):
    __fields__ = {
        'auth': bool,
        'name': str,
        'flair': int,   # index
        'degree': int,
        'score': int,
        'points': int,  # rank points
        'team': int,    # at start of match; 1 = red, 2 = blue, 0 = join late
        'events': Blob,
    }

    def __init__(self, data):
        super(Player, self).__init__(data)

        self.__stats__ = None

    @property
    def stats(self):
        if self.__stats__ is None:
            handler = PlayerStatCounter()
            self.parse_events(handler)
            self.__stats__ = handler
        return self.__stats__

    def parse_events(self, handler):
        parse_player(self.events, self.team,
                     self.__parent__.duration, handler=handler)

    def __lt__(self, other):
        """
        Necessary for building a heap of events.
        This obviously does not actually work.
        """
        return False


class Team(JsonObject):
    __fields__ = {
        'name': str,
        'score': int,
        '__splats__': Blob
    }

    def __init__(self, data):
        super(Team, self).__init__(data)

        self.__splatlist__ = None

    @property
    def splats(self):
        if self.__splatlist__ is None:
            handler = SplatsSaver()

            width = self.__parent__.map.width
            height = self.__parent__.map.height

            parse_splats(self.__splats__, width, height, handler=handler)
            self.__splatlist__ = handler.splatlist

        return self.__splatlist__


class ListOf:
    def __init__(self, t):
        self.type = t

    def __call__(self, data):
        return list(map(self.type, data))


class Match(JsonObject):
    __fields__ = {
        'server': str,              # Domain name of the game server
        'port': int,
        'official': bool,           # Played on an "official" server
        'group': str,               # Group ID
        # Start of the match
        'date': datetime.datetime.fromtimestamp,
        'timeLimit': int,           # In minutes
        'duration': int,            # In frames
        'finished': bool,
        'map': Map,                 # Map object
        'players': ListOf(Player),  # Array of player objects
        'teams': ListOf(Team),      # Array of team objects
    }

    def create_timeline(self, sort=False):
        heap = []

        for player in self.players:
            handler = PlayerEventLogger(heap, player)
            player.parse_events(handler)

        if sort:
            return sorted(heap)
        return heap

    def print_timeline(self):
        timeline = self.create_timeline()

        while timeline:
            time, event, player = heapq.heappop(timeline)
            print(f'{format_time(time)} | {player.name:<12} | {event}')
