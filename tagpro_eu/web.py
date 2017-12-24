import requests

import tagpro_eu.core


def download_match(id):
    r = requests.get(f'https://tagpro.eu/?download={id}')
    return tagpro_eu.core.Match(r.json())
