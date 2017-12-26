def format_time(frames):
    m, s = divmod(frames, 3600)
    s /= 60

    return f'{m:0>2}:{s:0>5.2f}'
