class MapHandler:
    # flake8: noqa
    def height(self, new_y): pass
    def tile(self, new_x, y, tile): pass


class MapSaver(MapHandler):
    def __init__(self):
        self.tiles = []

    def height(self, y):
        self.tiles.append([])

    def tile(self, x, y, tile):
        self.tiles[y].append(tile)
