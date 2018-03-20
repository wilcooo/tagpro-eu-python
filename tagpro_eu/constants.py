from enum import IntEnum, IntFlag


# Teams
class Team(IntEnum):
    """
    The team a player can be on. Actual names of teams can be discovered from
    their corresponding Team objects.
    """
    none = 0
    red = 1
    blue = 2

    def __str__(self):
        if self == Team.none:
            return "No team"
        elif self == Team.red:
            return "Red"
        elif self == Team.blue:
            return "Blue"

    def __eq__(self, other):
        if isinstance(other, Team):
            return super().__eq__(other)
        else:
            return other.__eq__(self)


# Flags
class Flag(IntEnum):
    """
    The flag a player can be holding.
    """
    none = 0
    opponent = 1
    opponent_potato = 2
    neutral = 3
    neutral_potato = 4
    temp = 5

    def __str__(self):
        if self == Flag.none:
            return 'No flag'
        elif self == Flag.opponent:
            return 'Opponent flag'
        elif self == Flag.opponent_potato:
            return 'Opponent potato'
        elif self == Flag.neutral:
            return 'Neutral flag'
        elif self == Flag.neutral_potato:
            return 'Neutral potato'
        elif self == Flag.temp:
            return 'Temporary flag'

    def is_potato(self):
        """
        Return whether or not a flag is a potato.

        :return: whether or not the flag is a potato
        """
        return self in (Flag.opponent_potato, Flag.neutral_potato)

    def is_opponent(self):
        """
        Return whether or not a flag is the opponent's.

        :return: whether or not the flag is the opponent's
        """
        return self in (Flag.opponent, Flag.opponent_potato)

    def is_neutral(self):
        """
        Return whether or not a flag is a neutral flag.

        :return: whether or not the flag is a neutral flag
        """
        return self in (Flag.neutral, Flag.neutral_potato)


# Powerups
class Powerup(IntFlag):
    """
    The powerups a player can have. This is a flag enum, so values can be
    combined using | or +.
    """
    none = 0
    juke_juice = 1
    rolling_bomb = 2
    tagpro = 4
    top_speed = 8
    all = 15

    def __str__(self):
        if self == Powerup.none:
            return 'No powerups'
        elif self == Powerup.juke_juice:
            return 'Juke Juice'
        elif self == Powerup.rolling_bomb:
            return 'Rolling Bomb'
        elif self == Powerup.tagpro:
            return 'TagPro'
        elif self == Powerup.top_speed:
            return 'Top Speed'
        else:
            return ', '.join(str(p)
                             for p in Powerup.enumerate()
                             if self & p > 0)

    @classmethod
    def enumerate(cls):
        """
        Yield all four distinct powerups a player can have.

        :returns: the four powerups
        """
        yield from (
            Powerup.juke_juice,
            Powerup.rolling_bomb,
            Powerup.tagpro,
            Powerup.top_speed
        )


# Tiles
class Tile(IntEnum):
    """
    A tile on a map.
    """
    empty = 0

    wall = 10
    wall_ll = 11
    wall_ul = 12
    wall_ur = 13
    wall_lr = 14

    floor = 20

    team_red = 110
    team_blue = 120
    team_neutral = 230

    flag_red = 30
    flag_blue = 40
    flag_neutral = 160

    potato_red = 190
    potato_blue = 200
    potato_neutral = 210

    flag_temp = 161

    boost = 50
    boost_red = 140
    boost_blue = 150

    bomb = 100

    spike = 70

    powerup = 60
    juke_juice = 61
    rolling_bomb = 62
    tagpro = 63
    top_speed = 64

    button = 80

    gate_open = 90
    gate_green = 91
    gate_red = 92
    gate_blue = 93

    protal_entry = 130
    portal_exit = 131

    endzone_red = 170
    endzone_blue = 180

    marsball = 211

    gravity_well = 220


# Flairs
class Flair(IntEnum):
    """
    A flair a player can use.
    """
    none = 0

    leaderboard_day = 1
    leaderboard_week = 2
    leaderboard_month = 3

    winrate_55 = 4
    winrate_65 = 5
    winrate_75 = 6

    donor_10 = 18
    donor_40 = 20
    donor_100 = 21
    donor_200 = 24
    donor_btc = 25

    developer = 19
    community_contributor = 17
    contest_winner = 22
    moderator = 7
    maptester = 8

    kongregate = 23

    birthday_1 = 33
    birthday_2a = 40
    birthday_2b = 41
    birthday_3a = 55
    birthday_3b = 56
    birthday_4a = 72
    birthday_4b = 73
    birthday_4c = 74

    st_patricks_1 = 34
    st_patricks_2 = 42
    st_patricks_3 = 57

    april_1 = 35
    april_2 = 43

    easter_1 = 36
    easter_2a = 49
    easter_2b = 50
    easter_3a = 58
    easter_3b = 59
    easter_3c = 65
    easter_4a = 44
    easter_4b = 45

    unfortunatesniper = 37

    halloween_1a = 38
    halloween_1b = 39
    halloween_2a = 52
    halloween_2b = 53
    halloween_2c = 54
    halloween_3a = 66
    halloween_3b = 67
    halloween_3c = 68
    halloween_4a = 75
    halloween_4b = 76
    halloween_4c = 77

    lgbt = 51

    christmas_1a = 69
    christmas_1b = 70
    christmas_1c = 71

    degree_2 = 116
    degree_6 = 81
    degree_9 = 117
    degree_11 = 82
    degree_17 = 104
    degree_32 = 83
    degree_42 = 84
    degree_51 = 85
    degree_57 = 118
    degree_66 = 86
    degree_69 = 87
    degree_79 = 105
    degree_88 = 88
    degree_98 = 89
    degree_100 = 90
    degree_101 = 97
    degree_110 = 119
    degree_123 = 98
    degree_130 = 106
    degree_143 = 99
    degree_151 = 100
    degree_168 = 101
    degree_180 = 102
    degree_196 = 103
    degree_206 = 121
    degree_212 = 91
    degree_220 = 120
    degree_238 = 107
    degree_276 = 115
    degree_300 = 113
    degree_314 = 114
