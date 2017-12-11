class SplatsHandler:
    def splats(self, splats, index): pass


class SplatsLogger(SplatsHandler):
    def splats(self, splats, index):
        for x, y in splats:
            print(f'{index}: ({x}, {y})')
