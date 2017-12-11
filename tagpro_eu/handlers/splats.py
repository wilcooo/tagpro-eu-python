class SplatsHandler:
    def splats(self, splats, time): pass


class SplatsLogger(SplatsHandler):
    def splats(self, splats, time):
        for x, y in splats:
            print(f'{time}: ({x}, {y})')
