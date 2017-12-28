from tagpro_eu.util import Time
import unittest


class TestTime(unittest.TestCase):
    def test_int(self):
        self.assertEqual(Time(0), 0)
        self.assertNotEqual(Time(0), 1)

    def test_arithmetic(self):
        self.assertEqual(Time(1) + Time(2), Time(3))
        self.assertEqual(Time(10) - Time(3), Time(7))

        self.assertIsInstance(Time(1) + Time(2), Time)
        self.assertIsInstance(Time(2) - Time(1), Time)

    def test_constructors(self):
        self.assertEqual(Time(60), Time.from_seconds(1))
        self.assertEqual(Time(7200), Time.from_minutes(2))
        self.assertEqual(Time.from_seconds(180), Time.from_minutes(3))

    def test_properties(self):
        self.assertEqual(Time.from_seconds(10).seconds, 10)
        self.assertEqual(Time.from_minutes(10).minutes, 10)
        self.assertEqual(Time().seconds, 0)
        self.assertEqual(Time().minutes, 0)

    def test_str(self):
        self.assertEqual(str(Time(0)), '00:00.00')
        self.assertEqual(str(Time.from_seconds(30)), '00:30.00')
        self.assertEqual(str(Time.from_minutes(5)), '05:00.00')
        self.assertEqual(str(Time(3900)), '01:05.00')
        self.assertEqual(str(Time(90)), '00:01.50')
