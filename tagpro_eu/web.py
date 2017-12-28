import re
import requests

import tagpro_eu.core


def download_match(id):
    """
    Download the match from tagpro.eu with the given ID, and return it as a
    Match object.

    This method should probably not be called too many times, as it makes
    requests to tagpro.eu. If you have to download multiple matches, consider
    using a bulk file, which you can (manually) download on
    https://tagpro.eu/?science. The module tagpro_eu.core has methods for
    loading those.

    :param id: the match ID
    :returns: the corresponding Match object
    """
    r = requests.get(f'https://tagpro.eu/?download={id}')
    return tagpro_eu.core.Match(r.json())


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
    match = re.match(match_url_regex, url)
    if match is not None:
        return int(match.group(5))
    else:
        return None
