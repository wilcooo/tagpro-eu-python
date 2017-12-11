import datetime
import json

from tagpro_eu.blob import Blob


class JsonObject:
    def __init__(self, data):
        for f, t in self.__class__.fields.items():
            value = data.get(f, None)

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
        'tiles': Blob,
    }


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
        'splats': Blob
    }


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
