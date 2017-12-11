import datetime
import json

from tagpro_eu.blob import Blob
from tagpro_eu.handlers.map import MapSaver
from tagpro_eu.handlers.splats import SplatsSaver
from tagpro_eu.parsers import parse_map
from tagpro_eu.parsers import parse_splats


class JsonObject:
    def __init__(self, data):
        for f, t in self.__class__.fields.items():
            value = data.get(f.strip('_'), None)

            if value is not None:
                value = t(value)

            setattr(self, f, value)

    @classmethod
    def from_string(cls, s):
        return cls(json.loads(s))

    @classmethod
    def from_file(cls, filename):
        with open(filename) as f:
            return cls(json.load(f))


class Map(JsonObject):
    fields = {
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
        self.__height__ = None

    @property
    def tiles(self):
        if self.__tilemap__ is None:
            self.parse_tiles()

        return self.__tilemap__

    @property
    def height(self):
        if self.__height__ is None:
            self.parse_tiles()

        return self.__height__

    def parse_tiles(self):
        handler = MapSaver()
        parse_map(self.__tiles__, self.width, handler=handler)

        self.__tilemap__ = handler.tiles
        self.__height__ = len(self.__tilemap__)


class Player(JsonObject):
    fields = {
        'auth': bool,
        'name': str,
        'flair': int,   # index
        'degree': int,
        'score': int,
        'points': int,  # rank points
        'team': int,    # at start of match; 1 = red, 2 = blue, 0 = join late
        'events': Blob,
    }


class Team(JsonObject):
    fields = {
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
            # TODO find correct size
            parse_splats(self.__splats__, 0, 0, handler=handler)
            self.__splatlist__ = handler.splatlist

        return self.__splatlist__


def ListOf(t):
    def inner(objs):
        return list(map(t, objs))

    return inner


class Match(JsonObject):
    fields = {
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
