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
