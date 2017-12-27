import datetime
import heapq
import json

from tagpro_eu.blob import Blob
from tagpro_eu.readers.map import MapReader
from tagpro_eu.readers.player import PlayerEventLogger, PlayerStats
from tagpro_eu.readers.splats import SplatsReader
from tagpro_eu.parsers import parse_map, parse_player, parse_splats
from tagpro_eu.util import format_time


def bulk_matches(filename, maps=None):
    """
    Read a file containing bulk match data, and yield the matches.
    A bulk file can be downloaded from https://tagpro.eu/?science

    The tagpro.eu bulk file is a JSON object mapping Match objects to their
    MatchId values. The MatchId is added as the property match_id in the
    yielded Match objects.

    If you want, you can supply a maps object (also as downloaded from
    tagpro.eu) to fill map data from. This object can be loaded using the
    bulk_maps method.

    :param filename: the name of the file to read matches from
    :param maps: the maps object (omit if undesired)
    :returns: the matches contained in the file
    """
    with open(filename) as f:
        data = json.load(f)
        for k, v in data.items():
            match = Match(v)
            match.match_id = k
            match.map_id = v['mapId']
            if maps is not None:
                match.map = maps[match.map_id]
            yield match


def bulk_maps(filename):
    """
    Read a file and return a maps object to be used in bulk_matches.
    The bulk maps file can be downloaded from https://tagpro.eu/?science

    :param filename: the name of the file to read maps from
    :returns: the maps object
    """
    with open(filename) as f:
        data = json.load(f)
        return {int(k): Map(v) for k, v in data.items()}


class JsonObject:
    """
    A data entity to be read from a tagpro.eu JSON file.

    Subclasses of JsonObject should define a __fields__ attribute, which is a
    dict mapping field names (as specified in the JSON format) to a
    constructor of the value. When initializing a JsonObject with some data,
    the values of these fields will be stored to attributes of the resulting
    object.

    If a key in __fields__ has underscores around it, these will be omitted
    when reading from the JSON data, but not for storing the attribute. This
    is useful if you want to define your own attribute with that name.
    """
    def __init__(self, data, strict=False):
        """
        Initialize a JsonObject using a dict of data loaded from a json file.
        When in strict mode, the method will fail when it encounters a missing
        key or wrong data type in the json data. If strict mode is disabled,
        these values will be set to None.

        :param data: dict of loaded json data for this object
        :param strict: whether or not to use strict mode
        :returns: the loaded JsonObject
        :raises KeyError: when strict mode is enabled and a missing key is
        found
        :raises TypeError: when strict mode is enabled and an element has the
        wrong data type
        """
        for f, t in self.__fields__.items():
            try:
                value = t(data[f.strip('_')])
            except (KeyError, TypeError):
                if strict:
                    raise
                value = None

            if isinstance(value, JsonObject):
                value.__parent__ = self
            elif isinstance(value, list):
                for item in value:
                    item.__parent__ = self

            setattr(self, f, value)

    @classmethod
    def from_string(cls, s, strict=False):
        """
        Load a JsonObject from a json string.

        :param s: the json string to load from
        :param strict: whether or not to use strict mode
        :returns: the loaded JsonObject
        :raises KeyError: when strict mode is disabled and a missing key is
        found
        :raises TypeError: when strict mode is disabled and an element has the
        wrong data type
        """
        return cls(json.loads(s), strict=strict)

    @classmethod
    def from_file(cls, filename, strict=False):
        """
        Load a JsonObject from a json file.

        :param filename: the name of the json file to load from
        :param strict: whether or not to use strict mode
        :returns: the loaded JsonObject
        :raises KeyError: when strict mode is disabled and a missing key is
        found
        :raises TypeError: when strict mode is disabled and an element has the
        wrong data type
        """
        with open(filename) as f:
            return cls(json.load(f), strict=strict)

    def __repr__(self):
        return 'JsonObject()'

    def to_dict(self):
        """
        Return a dict containing the data stored in this JsonObject. For a
        JsonObject o the following should hold:

            o == o.__class__(o.to_dict())

        :returns: the corresponding dict
        """
        def f(x):
            if isinstance(x, JsonObject):
                return x.to_dict()
            elif isinstance(x, list):
                return list(map(JsonObject.to_dict, x))
            elif isinstance(x, datetime.datetime):
                return int(x.strftime('%s'))
            elif isinstance(x, Blob):
                return x.to_string()
            else:
                return x

        return {field.strip('_'): f(getattr(self, field))
                for field in self.__fields__}

    def to_json(self):
        return json.dumps(self.to_dict())


class Map(JsonObject):
    """
    Represents a map object in tagpro.eu match files.
    The exact format can be found on https://tagpro.eu/?science
    """
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
        """
        Return the 2D array of tiles on this map. This is lazy-loaded from
        the blob in __tiles__ and then stored in __tilemap__.

        :returns: the tiles on the map
        """
        if self.__tilemap__ is None:
            self.parse_tiles()

        return self.__tilemap__

    @property
    def height(self):
        """
        Return the height of the map. Unlike width, this is not stored in the
        JSON format, and is therefore lazy-loaded together with tiles.

        :returns: the height of the map in tiles
        """
        if self.__tilemap__ is None:
            self.parse_tiles()

        return len(self.__tilemap__)

    def parse_tiles(self):
        """
        Load __tilemap__ from the __tiles__ blob, to be used by the tiles and
        height properties.
        """
        handler = MapReader()
        parse_map(self.__tiles__, self.width, handler=handler)

        self.__tilemap__ = handler.tiles

    def __repr__(self):
        return f'Map(name={self.name!r})'


class Player(JsonObject):
    """
    Represents a player object in tagpro.eu match files.
    The exact format can be found on https://tagpro.eu/?science
    """
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
        """
        Return a PlayerStats object corresponding to the player's stats. This
        is lazy-loaded from the events blob.

        :returns: the PlayerStats object for this player
        """
        if self.__stats__ is None:
            handler = PlayerStats()
            self.parse_events(handler)
            self.__stats__ = handler
        return self.__stats__

    def parse_events(self, handler):
        """
        Parse the events blob using the given reader.

        :param handler: the PlayerEventHandler object used to read the events
        """
        parse_player(self.events, self.team,
                     self.__parent__.duration, handler=handler)

    def __lt__(self, other):
        """
        Necessary for building a heap of events.
        This obviously does not actually work.
        """
        return False

    def __repr__(self):
        return f'Player(name={self.name!r})'


class Team(JsonObject):
    """
    Represent a team object in tagpro.eu match files.
    The exact format can be found on https://tagpro.eu/?science
    """
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
        """
        Return a list of splats on the map for this team. This is lazy-loaded
        from the __splats__ blob.

        :returns: list of splats
        """
        if self.__splatlist__ is None:
            handler = SplatsReader()

            width = self.__parent__.map.width
            height = self.__parent__.map.height

            parse_splats(self.__splats__, width, height, handler=handler)
            self.__splatlist__ = handler.splatlist

        return self.__splatlist__

    def __repr__(self):
        return f'Team(name={self.name!r})'


class ListOf:
    """
    Helper to serve as a constructor for lists in JsonObjects, that
    contain another type to be parsed. Essentially this is a curried version
    of map:

        ListOf(t)(d) = map(t, d)
    """
    def __init__(self, t):
        """
        :param t: the constructor to use on the list's elements
        """
        self.type = t

    def __call__(self, data):
        return list(map(self.type, data))


class Match(JsonObject):
    """
    Represents a match object in tagpro.eu match files.
    The exact format can be found on https://tagpro.eu/?science
    """
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
            print(f'{format_time(time)} | {player.name:<12} | {event}')

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

        non_stat_attrs = ('name', 'score')
        time_formatted_fields = ('time', 'hold', 'prevent', 'button', 'block')

        def format_field(p, field):
            if field in non_stat_attrs:
                v = getattr(p, field)
            else:
                v = getattr(p.stats, field)

            p = format_time(v) if field in time_formatted_fields else str(v)
            return p.center(field_width(field))

        def field_name(field):
            return 'Powerups' if field == 'pups_total' else field.title()

        def field_width(field):
            return 12 if field == 'name' else 8

        if sort_key is None:
            sort_key = default_sort

        if fields is None:
            fields = ['name', 'score', 'time', 'tags', 'pops', 'grabs',
                      'drops', 'hold', 'captures', 'returns', 'prevent',
                      'button', 'block', 'pups_total']

        print('|'.join(field_name(f).center(field_width(f)) for f in fields))
        print('-'.join('-' * field_width(f) for f in fields))

        for p in sorted(self.players, key=sort_key):
            print('|'.join(format_field(p, f) for f in fields))
