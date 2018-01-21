import re
import requests

import tagpro_eu.match


def download_match(url=None, id=None, raw_url=None):
    """
    Download the match with the given ID or URL, and return it as a Match
    object.

    - If id is given, the match will be downloaded from tagpro.eu
    - If url is given, the match ID will be extracted from it
      - If this succeeds, the match with given ID will be downloaded from
        tagpro.eu
      - Otherwise, it will attempt to directly download the data from url,
        or raw_url if it was given
    - If raw_url is given, the data will be directly downloaded from there

    Note that a single match ID as url will also succeed. If you take match
    URLs as user input, you can usually just pass it as url parameter, which
    will work for match links, download links, match IDs and raw data links
    for matches hosted elsewhere.

    This method should probably not be called too many times, as it makes
    requests to tagpro.eu. If you have to download multiple matches, consider
    using a bulk file, which you can (manually) download on
    https://tagpro.eu/?science. The module tagpro_eu.bulk has methods for
    loading those.

    :param id: a match ID
    :param url: a tagpro.eu match URL
    :param raw_url: a direct link to raw data that doesn't have to be on
    tagpro.eu
    :returns: the corresponding Match object
    :raises ValueError: when no valid id, url or raw_url was given
    """
    if id is None and url is not None:
        id = match_url_to_id(url)

        # if match_url_to_id didn't work and raw_url isn't set already,
        # we will use url as raw_url
        if raw_url is None:
            raw_url = url

    if id is not None:
        raw_url = f'https://tagpro.eu/?download={id}'

    if raw_url is None:
        raise ValueError("No valid match ID or URL was given")

    r = requests.get(raw_url)
    return tagpro_eu.match.Match(r.json())


match_url_regex =\
    r'^((https?://)?(www\.)?tagpro\.eu/?\?(download|match)=)?(\d+)$'


def match_url_to_id(url):
    """
    Converts a tagpro.eu match URL to the integer ID of that match.
    The URL can be a match page (/?match={id}), a raw data download link
    (/?download={id}), or just an ID.

    :param url: the URL to extract the ID from
    :returns: the ID of the match, or None if the URL didn't match
    """
    match = re.match(match_url_regex, str(url))
    if match is not None:
        return int(match.group(5))
    else:
        return None
