#!/usr/bin/env python3

"""
Using the built-in function, pretty-print the scoreboard of a TagPro game.
Can take a TagPro Analytics URL, ID, or raw data URL (such as raw pastebin or
gist) as input.
"""

import tagpro_eu
import sys


if len(sys.argv) >= 2:
    link = sys.argv[1]
else:
    link = input('Input a match URL or ID: ')

match = tagpro_eu.web.download_match(link)

# You can give sort_key and fields as keyword arguments, to customize the
# ordering and columns of the scoreboard. By default, it is ordered by score
# descending:

#    lambda p: -p.score
match.print_scoreboard()
