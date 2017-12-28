from tagpro_eu.blob import Blob
import base64
import unittest


class TestBlob(unittest.TestCase):
    def test_base64(self):
        data = bytes([0b0, 0b1, 0b10, 0b11, 0b100])
        blob = Blob.from_b64(base64.b64encode(data))
        self.assertEqual(blob.data, data)

    def test_read_bool(self):
        data = bytes([0b01001011])
        blob = Blob(data)
        self.assertEqual(blob.read_bool(), 0)
        self.assertEqual(blob.read_bool(), 1)
        self.assertEqual(blob.read_bool(), 0)
        self.assertEqual(blob.read_bool(), 0)
        self.assertEqual(blob.read_bool(), 1)
        self.assertEqual(blob.read_bool(), 0)
        self.assertEqual(blob.read_bool(), 1)
        self.assertEqual(blob.read_bool(), 1)

    def test_read_fixed(self):
        data = bytes([0b11010101, 0b11110010, 0b10010101])
        blob = Blob(data)
        self.assertEqual(blob.read_fixed(1), 0b1)
        self.assertEqual(blob.read_fixed(3), 0b101)
        self.assertEqual(blob.read_fixed(2), 0b01)
        self.assertEqual(blob.read_fixed(4), 0b0111)
        self.assertEqual(blob.read_fixed(8), 0b11001010)
        self.assertEqual(blob.read_fixed(6), 0b010101)

    def test_read_tally(self):
        data = bytes([0b11101011, 0b11001010])
        blob = Blob(data)
        self.assertEqual(blob.read_tally(), 3)
        self.assertEqual(blob.read_tally(), 1)
        self.assertEqual(blob.read_tally(), 4)
        self.assertEqual(blob.read_tally(), 0)
        self.assertEqual(blob.read_tally(), 1)
        self.assertEqual(blob.read_tally(), 1)

    def test_reset(self):
        data = bytes([0b10000000])
        blob = Blob(data)
        self.assertEqual(blob.read_bool(), 1)
        blob.reset()
        self.assertEqual(blob.pos, 0)
        self.assertEqual(blob.read_bool(), 1)
