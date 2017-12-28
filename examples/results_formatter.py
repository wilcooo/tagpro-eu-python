#!/usr/bin/env python3

"""
This script will take two match links as input, and print a markdown results
post, much like the ones seen on r/ELTP
"""

import tagpro_eu.web

url1 = input('Half 1: ')
url2 = input('Half 2: ')

h1 = tagpro_eu.web.download_match(url=url1)
h2 = tagpro_eu.web.download_match(url=url2)

switched_in_second_half = None  # "Uncertain"

t1 = h1.teams[0].name
t2 = h1.teams[1].name

if t1 != 'Red' and t2 != 'Blue':
    if h2.teams[0].name == t1 and h2.teams[1].name == t2:
        switched_in_second_half = False
    elif h2.teams[0].name == t2 and h2.teams[1].name == t1:
        switched_in_second_half = True

if switched_in_second_half is None:
    p1 = filter(lambda p: p.team == 0, h1.players)
    p2 = filter(lambda p: p.team == 1, h1.players)

    def find_player(match, player):
        for p in match.players:
            if p.name == player:
                return p
        return None

    def plays_on_team_h2(player, team):
        p = find_player(h2, player.name)
        if p is None:
            return False
        return p.team == team

    def number_on_team_h2(players, team):
        c = 0
        for p in players:
            if plays_on_team_h2(p, team):
                c += 1
        return c

    stayed = number_on_team_h2(p1, 1) + number_on_team_h2(p2, 0)
    switched = number_on_team_h2(p1, 0) + number_on_team_h2(p2, 1)

    if stayed > switched:
        switched_in_second_half = False
    elif switched > stayed:
        switched_in_second_half = True
    else:  # Give up and ask the user
        print("Did teams switch between halves? (y/n)")
        inp = input().lower()
        switched_in_second_half = inp.startswith('y')

s11 = h1.teams[0].score
s12 = h1.teams[1].score

s21 = h2.teams[0].score
s22 = h2.teams[1].score

if switched_in_second_half:
    s21, s22 = s22, s21


def winner(s, t):
    if s > t:
        return t1
    elif t > s:
        return t2
    else:
        return 'Tie'


w1 = winner(s11, s12)
w2 = winner(s21, s22)

s1 = s11 + s21
s2 = s12 + s22

w = winner(s1, s2)


print(f'# {t1} vs {t2}: {s1}-{s2} {w}')
print(f'**H1:** [{s11}-{s12} {w1}]({url1})  ')
print(f'**H2:** [{s21}-{s22} {w2}]({url2})')
