import base64


class Blob:
    def __init__(self, data):
        self.data = base64.b64decode(data)
        self.pos = 0

    def end(self):
        return self.pos >> 3 >= len(self.data)

    def read_bool(self):
        res = 0
        if not self.end():
            res = self.data[self.pos >> 3] >> 7 - (self.pos & 7) & 1
        self.pos += 1
        return res

    def read_fixed(self, bits):
        res = 0
        for _ in range(bits):
            res = res << 1 | self.read_bool()
        return res

    def read_tally(self):
        res = 0
        while self.read_bool():
            res += 1
        return res

    def read_footer(self):
        size = self.read_fixed(2) << 3
        free = 8 - (self.pos & 7) & 7
        size |= free
        minimum = 0

        while free < size:
            minimum += 1 << free
            free += 8

        return self.read_fixed(size) + minimum
