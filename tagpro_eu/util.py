from tagpro_eu import constants


def format_time(frames):
    frames //= 60

    m, s = divmod(frames, 60)

    return f'{m:0>2}:{s:0>2}'


def format_powerups(powerups):
    ps = []

    if powerups & constants.JUKE_JUICE:
        ps.append('Juke Juice')

    if powerups & constants.ROLLING_BOMB:
        ps.append('Rolling Bomb')

    if powerups & constants.TAGPRO:
        ps.append('TagPro')

    if powerups & constants.TOP_SPEED:
        ps.append('Top Speed')

    return ', '.join(ps)


def flag_name(flag):
    if flag == constants.NO_FLAG:
        return 'No flag'
    elif flag == constants.OPP_FLAG:
        return 'Opponent flag'
    elif flag == constants.NEUTRAL_FLAG:
        return 'Neutral flag'
    elif flag == constants.OPP_POTATO_FLAG:
        return 'Opponent potato'
    elif flag == constants.NEUTRAL_POTATO_FLAG:
        return 'Neutral potato'
    elif flag == constants.TEMP_FLAG:
        return 'Temporary flag'
