from tagpro_eu import constants


def format_time(frames):
    frames //= 60

    m, s = divmod(frames, 60)

    return f'{m:2>0}:{s:2>0}'


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
