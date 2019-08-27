import json, ijson

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
    parser = ijson.parse(f)
    builder = ijson.ObjectBuilder()

    next(parser)
    match_id = next(parser)[2]

    for prefix, event, value in parser:
        if prefix: builder.event(event, value)
        else:
            match = Match(builder.value)
            match.match_id = match_id
            match.map_id = builder.value['mapId']
            if maps is not None:
                match.map = maps[match.map_id]
            builder = ijson.ObjectBuilder()
            match_id = value
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
