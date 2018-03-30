import datetime
import json

from tagpro_eu.blob import Blob


class JsonObject:
    """
    A data entity to be read from a tagpro.eu JSON file.

    Subclasses of JsonObject should define a __fields__ attribute, which is a
    dict mapping field names (as specified in the JSON format) to a
    constructor of the value. When initializing a JsonObject with some data,
    the values of these fields will be stored to attributes of the resulting
    object.

    If a key in __fields__ has underscores around it, these will be omitted
    when reading from the JSON data, but not for storing the attribute. This
    is useful if you want to define your own attribute with that name.
    """
    def __init__(self, data, strict=False):
        """
        Initialize a JsonObject using a dict of data loaded from a json file.
        When in strict mode, the method will fail when it encounters a missing
        key or wrong data type in the json data. If strict mode is disabled,
        these values will be set to None.

        :param data: dict of loaded json data for this object
        :param strict: whether or not to use strict mode
        :returns: the loaded JsonObject
        :raises KeyError: when strict mode is enabled and a missing key is
        found
        :raises TypeError, ValueError: when strict mode is enabled and an
        element has the wrong data type
        """
        for f, t in self.__fields__.items():
            try:
                value = t(data[f.strip('_')])
            except (KeyError, ValueError, TypeError):
                if strict:
                    raise
                value = None

            if isinstance(value, JsonObject):
                value.__parent__ = self
            elif isinstance(value, list):
                for item in value:
                    item.__parent__ = self

            setattr(self, f, value)

    @classmethod
    def from_string(cls, s, strict=False):
        """
        Load a JsonObject from a json string.

        :param s: the json string to load from
        :param strict: whether or not to use strict mode
        :returns: the loaded JsonObject
        :raises KeyError: when strict mode is disabled and a missing key is
        found
        :raises TypeError: when strict mode is disabled and an element has the
        wrong data type
        """
        return cls(json.loads(s), strict=strict)

    @classmethod
    def from_file(cls, filename, strict=False):
        """
        Load a JsonObject from a json file.

        :param filename: the name of the json file to load from
        :param strict: whether or not to use strict mode
        :returns: the loaded JsonObject
        :raises KeyError: when strict mode is disabled and a missing key is
        found
        :raises TypeError: when strict mode is disabled and an element has the
        wrong data type
        """
        with open(filename) as f:
            return cls(json.load(f), strict=strict)

    def __eq__(self, other):
        for f in self.__fields__.keys():
            if getattr(self, f) != getattr(other, f):
                return False
        return True

    def __repr__(self):
        return 'JsonObject()'

    def to_dict(self):
        """
        Return a dict containing the data stored in this JsonObject. For a
        JsonObject o the following should hold:

            o == o.__class__(o.to_dict())

        :returns: the corresponding dict
        """
        def f(x):
            if isinstance(x, JsonObject):
                return x.to_dict()
            elif isinstance(x, list):
                return list(map(JsonObject.to_dict, x))
            elif isinstance(x, datetime.datetime):
                return int(x.strftime('%s'))
            elif isinstance(x, Blob):
                return x.to_string()
            else:
                return x

        return {field.strip('_'): f(getattr(self, field))
                for field in self.__fields__}

    def to_json(self):
        return json.dumps(self.to_dict())


class ListOf:
    """
    Helper to serve as a constructor for lists in JsonObjects, that
    contain another type to be parsed. Each object in the created list has
    an index attribute, which corresponds to its index in the given list.
    """
    def __init__(self, t):
        """
        :param t: the constructor to use on the list's elements
        """
        self.type = t

    def __call__(self, data):
        out = []

        for i, d in enumerate(data):
            v = self.type(d)
            v.index = i
            out.append(v)

        return out
