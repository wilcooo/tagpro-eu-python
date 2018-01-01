import json

from tagpro_eu.map import Map
from tagpro_eu.match import Match


def load_matches(f, maps=None):
    """
    Read a file containing bulk match data, and yield the matches.
    A bulk file can be downloaded from https://tagpro.eu/?science

    The tagpro.eu bulk file is a JSON object mapping Match objects to their
    MatchId values. The MatchId is added as the property match_id in the
    yielded Match objects.

    If you want, you can supply a maps object (also as downloaded from
    tagpro.eu) to fill map data from. This object can be loaded using the
    load_maps method.

    :param f: a file descriptor to read matches from
    :param maps: the maps object (omit if undesired)
    :returns: the matches contained in the file
    """
    data = json.load(f)
    for k, v in data.items():
        match = Match(v)
        match.match_id = k
        match.map_id = v['mapId']
        if maps is not None:
            match.map = maps[match.map_id]
        yield match


def load_maps(f):
    """
    Read a file and return a maps object to be used in bulk_matches.
    The bulk maps file can be downloaded from https://tagpro.eu/?science

    :param f: a file descriptor to read maps from
    :returns: the maps object
    """
    data = json.load(f)
    return {int(k): Map(v) for k, v in data.items()}
