import json
import unittest
from .short_url import ShortURL
from ..errors import ToManyShortURL, NoSupportShortURLCharacter, NoSupportURL, InvalidInput


class TestStringMethods(unittest.TestCase):

    def test_url_is_valid(self):
        t1 = ShortURL()
        t1.init_by_create({"url": "http://google.com"})
        self.assertIsNone(t1.verify())

        t2 = ShortURL()
        t2.init_by_create({"url": "abcd"})
        try:
            t2.verify()
        except NoSupportURL as e:
            self.assertEqual(type(e), NoSupportURL)

    def test_encode(self):
        t1 = ShortURL()
        t1.short = "jU"
        num = t1.encode()
        self.assertEqual(num, 1234)

    def test_decode(self):
        t1 = ShortURL()
        t1.id = 1234
        ss = t1.decode()
        self.assertEqual(ss, "jU")


if __name__ == '__main__':
    unittest.main()
