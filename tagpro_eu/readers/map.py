class MapHandler:
    """
    Event handler for reading a map blob.
    You should probably not override this one, as simply accessing the tiles
    property in Map (which uses MapReader) is much easier.
    """
    # flake8: noqa
    def height(self, new_y): pass
    def tile(self, new_x, y, tile): pass


class MapReader(MapHandler):
    """
    Implementation of MapHandler that stores the read tiles to a 2D array.
    This array can be accessed from the tiles attribute.
    """
    def __init__(self):
        self.tiles = []

    def height(self, y):
        self.tiles.append([])

    def tile(self, x, y, tile):
        self.tiles[y].append(tile)
