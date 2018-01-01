import tagpro_eu.json
import tagpro_eu.match
import unittest


class JsonTestObject(tagpro_eu.json.JsonObject):
    __fields__ = {
        'foo': int,
        '__bar__': int
    }


class JsonTestObjectNested(tagpro_eu.json.JsonObject):
    __fields__ = {
        'inner': JsonTestObject
    }


class JsonTestObjectWithList(tagpro_eu.json.JsonObject):
    __fields__ = {
        'list': tagpro_eu.json.ListOf(JsonTestObject)
    }


class TestJsonObject(unittest.TestCase):
    def get_object(self):
        return JsonTestObject({'foo': 3, 'bar': 5})

    def test_init(self):
        o = self.get_object()
        self.assertEqual(o.foo, 3)

    def test_hidden_field(self):
        o = self.get_object()
        self.assertEqual(o.__bar__, 5)

    def test_strict(self):
        with self.assertRaises(KeyError):
            JsonTestObject({}, strict=True)

        with self.assertRaises(ValueError):
            JsonTestObject({'foo': 'bar', 'bar': 5}, strict=True)

    def test_not_strict(self):
        JsonTestObject({}, strict=False)
        JsonTestObject({'foo': 'bar', 'bar': 5}, strict=False)

    def test_to_dict(self):
        o = self.get_object()
        self.assertEqual(o, JsonTestObject(o.to_dict()))

    def test_equality(self):
        o = self.get_object()
        p = self.get_object()
        q = JsonTestObject({'foo': 3, 'bar': 6})
        self.assertEqual(o, p)
        self.assertNotEqual(o, q)
        self.assertNotEqual(p, q)


class TestJsonObjectNesting(unittest.TestCase):
    def nested_object(self):
        return JsonTestObjectNested({'inner': {'foo': 3}})

    def test_nesting(self):
        o = self.nested_object()
        self.assertEqual(o.inner.foo, 3)

    def test_parent(self):
        o = self.nested_object()
        self.assertEqual(o, o.inner.__parent__)

    def test_to_dict(self):
        o = self.nested_object()
        self.assertEqual(o, JsonTestObjectNested(o.to_dict()))


class TestJsonObjectList(unittest.TestCase):
    def list_object(self):
        return JsonTestObjectWithList({'list': [{'foo': 3}, {'foo': 4}]})

    def test_list(self):
        o = self.list_object()
        self.assertEqual(o.list[0].foo, 3)
        self.assertEqual(o.list[1].foo, 4)

    def test_index(self):
        o = self.list_object()
        self.assertEqual(o.list[0].index, 0)
        self.assertEqual(o.list[1].index, 1)

    def test_parent(self):
        o = self.list_object()
        self.assertEqual(o.list[0].__parent__, o)
        self.assertEqual(o.list[1].__parent__, o)

    def test_to_dict(self):
        o = self.list_object()
        self.assertEqual(o, JsonTestObjectWithList(o.to_dict()))


class TestMatch(unittest.TestCase):
    def test_player_in_team(self):
        match = tagpro_eu.match.Match({
            'players': [
                {'name': 'foo', 'team': 1},
                {'name': 'bar', 'team': 2}
            ],
            'teams': [
                {},
                {}
            ]
        })

        p1, p2 = match.players
        t1, t2 = match.teams

        self.assertNotEqual(p1, p2)
        self.assertNotEqual(t1, t2)

        self.assertIn(p1, t1.players)
        self.assertIn(p2, t2.players)
        self.assertNotIn(p1, t2.players)
        self.assertNotIn(p2, t1.players)

        self.assertEqual(p1.team, t1)
        self.assertEqual(p2.team, t2)
