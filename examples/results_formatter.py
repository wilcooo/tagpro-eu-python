#!/usr/bin/env python3

"""
This script will take two match links as input, and print a markdown results
post, much like the ones seen on r/ELTP
"""

from tagpro_eu.constants import Team
from tagpro_eu.web import download_match

url1 = input('Half 1: ')
url2 = input('Half 2: ')

h1 = download_match(url=url1)
h2 = download_match(url=url2)

switched_in_second_half = None  # "Uncertain"

t1 = h1.team_red.name
t2 = h1.team_blue.name

if t1 != 'Red' and t2 != 'Blue':
    if h2.team_red.name == t1 and h2.team_blue.name == t2:
        switched_in_second_half = False
    elif h2.team_red.name == t2 and h2.team_blue.name == t1:
        switched_in_second_half = True

if switched_in_second_half is None:
    p1 = h1.team_red.players
    p2 = h1.team_blue.players

    def find_player(match, player):
        for p in match.players:
            if p.name == player:
                return p
        return None

    def number_on_team_h2(players, team):
        c = 0
        for p in players:
            if p in h2.get_team(team).players:
                c += 1
        return c

    switched = number_on_team_h2(p1, Team.blue) +\
        number_on_team_h2(p2, Team.red)
    stayed = number_on_team_h2(p1, Team.red) +\
        number_on_team_h2(p2, Team.blue)

    if stayed > switched:
        switched_in_second_half = False
    elif switched > stayed:
        switched_in_second_half = True
    else:  # Give up and ask the user
        print("Did teams switch between halves? (y/n)")
        inp = input().lower()
        switched_in_second_half = inp.startswith('y')

s1r = h1.team_red.score
s1b = h1.team_blue.score

s2r = h2.team_red.score
s2b = h2.team_blue.score

if switched_in_second_half:
    s2r, s2b = s2b, s2r


def winner(s, t):
    if s > t:
        return t1
    elif t > s:
        return t2
    else:
        return 'Tie'


w1 = winner(s1r, s1b)
w2 = winner(s2r, s2b)

sr = s1r + s2r
sb = s1b + s2b

w = winner(sr, sb)


print(f'# {t1} vs {t2}: {sr}-{sb} {w}')
print(f'**H1:** [{s1r}-{s1b} {w1}]({url1})  ')
print(f'**H2:** [{s2r}-{s2b} {w2}]({url2})')
