class Time(int):
    """
    Represents an amount of time in-game.
    """
    @classmethod
    def seconds(cls, x):
        return cls(x * 60)

    @classmethod
    def minutes(cls, x):
        return cls(x * 3600)

    def __add__(self, other):
        return Time(super(Time, self).__add__(other))

    def __sub__(self, other):
        return Time(super(Time, self).__sub__(other))

    def __str__(self):
        """
        Format a time in in-game frames, to show minutes, seconds and
        centiseconds.

        :param frames: the time in frames
        :returns: the formatted time
        """
        m, s = divmod(self, 3600)
        s /= 60

        return f'{m:0>2}:{s:0>5.2f}'

    def __repr__(self):
        return str(self)
