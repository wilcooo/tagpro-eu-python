tagpro-eu-python
================

Description
-----------

This package provides an easy interface for reading match files downloaded from the stat-collection website tagpro.eu_ (by Ronding). Uses of this include, but are not limited to:

- Collecting individual players' stats from matches
- Pretty-printing the outcome of matches
- Outputting full match timelines
- Statistical analysis of TagPro matches
- Rendering maps

.. _tagpro.eu: https://www.tagpro.eu


Installation
------------

Install using pip (python 3.6+)::

  pip install tagpro-eu

Install from source::

  git clone git@github.com:arfie/tagpro-eu-python.git
  cd tagpro-eu-python
  sudo python3 setup.py install
  # or:  python3 setup.py install --user
  # to install for current user only


Quick Start
-----------

::

  >>> import tagpro_eu

Download an online match with ID 1743331_. Instead of the ID, a match URL or raw data URL can also be given. ::

  >>> match = tagpro_eu.download_match(1743331)
  >>> match
  Match(server='tagpro-radius.koalabeast.com', port=8003)

.. _1743331: https://www.tagpro.eu/?match=1743331

Find out basic match information::

  >>> match.date
  datetime.datetime(2018, 1, 19, 3, 47, 26)

Find out match results::

  >>> (match.team_red.score, match.team_blue.score)
  (1, 3)

Look up players::

  >>> match.players[7]
  Player(name='LiddiLidd')

Read player stats. Time values are automatically formatted, but are internally just integers representing a number of frames (1/60 of a second). ::

  >>> match.players[7].stats.captures
  2
  >>> match.players[7].stats.hold
  00:58.12

Access the match's map::

  >>> match.map
  Map(name='Constriction')
  >>> (match.map.width, match.map.height)
  (59, 25)

Read the map tiles as a 2D array::

  >>> match.map.tiles[20][8]
  <Tile.flag_red: 30>
