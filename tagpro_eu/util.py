class Time(int):
    """
    Represents an amount of time in-game.
    Casting to int will give the number of frames.
    """
    @classmethod
    def from_seconds(cls, x):
        """
        Create a Time from a number of seconds.
        """
        return cls(x * 60)

    @classmethod
    def from_minutes(cls, x):
        """
        Create a Time from a number of minutes.
        """
        return cls(x * 3600)

    @property
    def seconds(self):
        """
        The number of seconds in this time, discarding the remainder frames.
        """
        return self // 60

    @property
    def minutes(self):
        """
        The number of minutes in this time, discarding the remainder seconds
        and frames.
        """
        return self // 3600

    def __add__(self, other):
        return Time(super().__add__(other))

    def __sub__(self, other):
        return Time(super().__sub__(other))

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
