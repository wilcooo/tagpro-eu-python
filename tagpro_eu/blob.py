import base64


class Blob:
    """
    A blob object as loaded from a json object. The exact format can be found
    on https://tagpro.eu/?science.
    """
    def __init__(self, data):
        """
        Initialize a blob with the given bytestring as data.

        :param data: the data for this blob
        """
        self.data = data
        self.pos = 0

    @classmethod
    def from_b64(cls, b64data):
        """
        Initialize a blob with the given base64-encoded data.

        :param data: the base64-encoded data for this blob
        """
        return cls(base64.b64decode(b64data))

    def end(self):
        """
        Return whether or not the pointer has reached the end of the blob.

        :returns: whether or not reading is finished
        """
        return self.pos >> 3 >= len(self.data)

    def read_bool(self):
        """
        Read one boolean from the blob.

        This code is translated from the PHP implementation on
        https://tagpro.eu/?science.

        :returns: the boolean read from the blob
        """
        res = 0
        if not self.end():
            res = self.data[self.pos >> 3] >> 7 - (self.pos & 7) & 1
        self.pos += 1
        return res

    def read_fixed(self, bits):
        """
        Read one n-bit integer from the blob.

        This code is translated from the PHP implementation on
        https://tagpro.eu/?science.

        :param bits: the number of bits the integer fits in
        :returns: the integer read from the blob
        """
        res = 0
        for _ in range(bits):
            res = res << 1 | self.read_bool()
        return res

    def read_tally(self):
        """
        Read a tally (arbitrarily large unsigned integer) from the blob.

        This code is translated from the PHP implementation on
        https://tagpro.eu/?science.

        :returns: the tally read from the blob
        """
        res = 0
        while self.read_bool():
            res += 1
        return res

    def read_footer(self):
        """
        Read a footer (unsigned integer) from the blob.

        This code is translated from the PHP implementation on
        https://tagpro.eu/?science.

        :returns: the footer read from the blob
        """
        size = self.read_fixed(2) << 3
        free = 8 - (self.pos & 7) & 7
        size |= free
        minimum = 0

        while free < size:
            minimum += 1 << free
            free += 8

        return self.read_fixed(size) + minimum

    def reset(self):
        """
        Reset the pointer to the start of the blob.
        """
        self.pos = 0

    def __repr__(self):
        return 'Blob()'

    def to_string(self):
        """
        base64-encode the blob data.

        :returns: the base64-encoded blob data
        """
        return base64.b64encode(self.data).decode('ascii')
