class SplatsHandler:
    """
    Event handler for reading a team's splats blob.
    You should probably not override this one, as simply accessing the splats
    property in Team (which uses SplatsReader) is much easier.
    """
    def splats(self, splats, index): pass


class SplatsReader(SplatsHandler):
    """
    Implementation of SplatsHandler that stores the read splats to an array.
    This array can be accessed from the splatlist attribute.

    Each element in the array is a tuple with (x, y) coordinates. These are in
    pixels, measured from the center of the top-left tile on the map. Each tile
    is 40×40 pixels.
    """
    def __init__(self):
        self.splatlist = []

    def splats(self, splats, index):
        self.splatlist.extend(splats)
