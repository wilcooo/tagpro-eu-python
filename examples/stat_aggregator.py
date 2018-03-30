#!/usr/bin/env python3

"""
Takes one or more TagPro Analytics matches through standard input, then prints
a CSV file containing aggregated statistics for all players in those games.
"""

import tagpro_eu

import csv
import sys

from collections import defaultdict


links = []
inp = input()
while inp:
    links.append(inp)
    inp = input()

stats = defaultdict(tagpro_eu.player.PlayerStats)

for link in links:
    match = tagpro_eu.web.download_match(link)
    for player in match.players:
        stats[player.name] += player.stats

columns = [
    ('+/-', lambda s: s.cap_diff),
    ('time', lambda s: s.time // 60),
    ('tags', lambda s: s.tags),
    ('pops', lambda s: s.pops),
    ('grabs', lambda s: s.grabs),
    ('drops', lambda s: s.drops),
    ('hold', lambda s: s.hold // 60),
    ('captures', lambda s: s.captures),
    ('returns', lambda s: s.returns),
    ('prevent', lambda s: s.prevent // 60),
    ('pups', lambda s: sum(s.pups.values())),
    ('button', lambda s: s.button // 60),
    ('block', lambda s: s.block // 60),
]

wr = csv.writer(sys.stdout)
wr.writerow(['player'] + [t[0] for t in columns])

for p, s in stats.items():
    wr.writerow([p] + [t[1](s) for t in columns])
