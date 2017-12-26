class SplatsHandler:
    def splats(self, splats, index): pass


class SplatsReader(SplatsHandler):
    def __init__(self):
        self.splatlist = []

    def splats(self, splats, index):
        self.splatlist.extend(splats)


class SplatsLogger(SplatsHandler):
    def splats(self, splats, index):
        for x, y in splats:
            print(f'{index}: ({x}, {y})')
