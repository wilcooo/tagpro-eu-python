def format_time(frames):
    """
    Format a time in in-game frames, to show minutes, seconds and centiseconds.

    :param frames: the time in frames
    :returns: the formatted time
    """
    m, s = divmod(frames, 3600)
    s /= 60

    return f'{m:0>2}:{s:0>5.2f}'
