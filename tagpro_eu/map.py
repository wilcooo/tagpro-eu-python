from tagpro_eu.blob import Blob
from tagpro_eu.constants import Tile
from tagpro_eu.data import JsonObject


class Map(JsonObject):
    """
    Represents a map object in tagpro.eu match files.
    The exact format can be found on https://tagpro.eu/?science
    """
    __fields__ = {
        'name': str,
        'author': str,
        'type': str,        # ctf, nf, mb etc., empty for unofficial maps
        'marsballs': int,   # number
        'width': int,
        '__tiles__': Blob.from_b64,
    }

    def __init__(self, data, strict=False):
        super().__init__(data, strict=strict)

        self.__tilemap__ = None

    @property
    def tiles(self):
        """
        Return the 2D array of tiles on this map. This is lazy-loaded from
        the blob in __tiles__ and then stored in __tilemap__.

        :returns: the tiles on the map
        """
        if self.__tilemap__ is None:
            self._parse_tiles()

        return self.__tilemap__

    @property
    def height(self):
        """
        Return the height of the map. Unlike width, this is not stored in the
        JSON format, and is therefore lazy-loaded together with tiles.

        :returns: the height of the map in tiles
        """
        if self.__tilemap__ is None:
            self._parse_tiles()

        return len(self.__tilemap__)

    def _parse_tiles(self):
        """
        Load __tilemap__ from the __tiles__ blob, to be used by the tiles and
        height properties.
        """
        self.__tilemap__ = []

        blob = self.__tiles__
        blob.reset()

        x, y = 0, 0

        while not blob.end() or x > 0:
            tile = blob.read_fixed(6)
            if tile != Tile.empty:
                # idk
                if tile < 6:
                    tile += 9
                elif tile < 13:
                    tile = (tile - 4) * 10
                elif tile < 17:
                    tile += 77
                elif tile < 20:
                    tile = (tile - 7) * 10
                elif tile < 22:
                    tile += 110
                else:
                    tile = (tile - 8) * 10

            for i in range(blob.read_footer() + 1):
                if x == 0:
                    self.__tilemap__.append([])
                self.__tilemap__[y].append(Tile(tile))

                x += 1
                if x == self.width:
                    x = 0
                    y += 1

    def __eq__(self, other):
        """
        Equality of maps is determined by comparing tiles.

        Map might have multiple iterations, so just name(+author) won't work.
        Maps might be renamed, but still have the same tiles.
        Maps will probably have to be compared across matches, so comparing
        parents is not a good idea.
        """
        return other is not None and self.tiles == other.tiles

    def __repr__(self):
        return f'Map(name={self.name!r})'
