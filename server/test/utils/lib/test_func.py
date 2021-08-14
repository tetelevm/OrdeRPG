import random
from unittest import TestCase

from server.utils.lib.func import *


class Test(TestCase):
    def test_int_to_bytes(self):
        self.assertEqual(int_to_bytes(255), b'\xff')
        self.assertEqual(int_to_bytes(0), b'')
        self.assertEqual(int_to_bytes(-255), b'\xff')
        self.assertEqual(int_to_bytes(2**16 - 1), b'\xff\xff')
        self.assertEqual(int_to_bytes(400_000), b'\x06\x1a\x80')

    def test_str_to_bytes(self):
        self.assertEqual(str_to_bytes('test'), b'test')
        self.assertEqual(str_to_bytes('test' * 100), b'test' * 100)
        self.assertEqual(str_to_bytes(1), b'1')
        self.assertEqual(str_to_bytes([1, 2, 3, 4]), b'[1, 2, 3, 4]')
        self.assertEqual(str_to_bytes(''), b'')
        self.assertEqual(str_to_bytes(int), b"<class 'int'>")

    def test_with_randomize(self):
        # In theory, this test could break, but if it does, you're lucky :)

        def get_random_value():
            return random.randint(0, 10 ** 100)
        randomize_int = with_randomize(get_random_value)

        matches = sum((randomize_int() == randomize_int() for _ in range(5)))
        self.assertTrue(matches < 2)

        matches = 0
        for _ in range(5):
            random.seed(0)
            a = randomize_int()
            random.seed(0)
            b = randomize_int()
            matches += a == b
        self.assertTrue(matches < 2)

    def test_generate_random_string(self):
        self.assertEqual(type(generate_random_string(10)), str)
        self.assertEqual(len(generate_random_string(100)), 100)

        self.assertTrue(
            set(generate_random_string(100)).issubset(default_alphabet))

        another_alphabet = '~!@#$%^&*()_+'
        string = generate_random_string(100, another_alphabet)
        self.assertTrue(set(string).issubset(another_alphabet))

    def test_generate_random_advanced_string(self):
        self.assertEqual(type(generate_random_advanced_string(10)), str)
        self.assertEqual(len(generate_random_advanced_string(100)), 100)

        self.assertTrue(
            set(generate_random_string(100)).issubset(advanced_alphabet))

    def test_camel_to_snake(self):
        self.assertEqual(camel_to_snake('test_string'), 'test_string')
        self.assertEqual(camel_to_snake('TESTSTRING'), 'teststring')
        self.assertEqual(camel_to_snake('TestString'), 'test_string')
        self.assertEqual(camel_to_snake('LongLongTestString'), 'long_long_test_string')
        self.assertEqual(camel_to_snake('TESTString'), 'test_string')
        self.assertEqual(camel_to_snake('TestSTRING'), 'test_string')
        self.assertEqual(camel_to_snake('TEST_STRING'), 'test_string')
        self.assertEqual(camel_to_snake('TestString123'), 'test_string123')
        self.assertEqual(camel_to_snake('123TestString'), '123_test_string')
        self.assertEqual(camel_to_snake('1234567'), '1234567')
