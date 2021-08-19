import os
from tempfile import NamedTemporaryFile
from unittest import TestCase

from server.lib.classes import *
from server.lib.classes.hasher import Hasher, Shake, bstring_cycle


class Test(TestCase):
    def test_env_parser(self):
        os.environ['TEST_VALUE'] = '[1, 2, 3, 4]'
        self.assertEqual(
            env_parser.get_arg_from_environ('TEST_VALUE'), [1, 2, 3, 4])
        os.environ.pop('TEST_VALUE')

        file_text = b"""
            value = True
    
            # test string comment
            # next line have spaces
            
            value_2 = 'test string'
    
            raw_value = raw_value
        """
        with NamedTemporaryFile(delete=False) as file:
            file.write(file_text)

        self.assertEqual(
            env_parser.get_arg_from_file(['val', 'value', 'VALUE'], file.name),
            True
        )

        self.assertIn(file.name, env_parser._files_cache)

        self.assertEqual(
            env_parser.get_arg_from_file('value_2', file.name, default='another string'),
            'test string'
        )

        self.assertEqual(
            env_parser.get_arg_from_file('raw_value', file.name, translate=False),
            'raw_value'
        )

        with self.assertRaises(NameError):
            env_parser.get_arg_from_file('value_3', file.name)

        with self.assertRaises(ValueError):
                env_parser.get_arg_from_file('raw_value', file.name)

        self.assertEqual(
            env_parser.get_arg_from_file(
                'value_3', file.name, default='default value', translate=False),
            'default value'
        )

    def test_hasher(self):
        shake_24 = Shake(24)
        Hasher.set_algorithms([shake_24, 'sha3_256'])
        self.assertEqual(
            Hasher.hash_algs, [shake_24, Hasher.supported_algorithms['sha3_256']])

        Hasher.set_algorithms()
        self.assertEqual(
            Hasher.hash_algs,
            [Hasher.supported_algorithms['sha3_384'], Hasher.supported_algorithms['blake2b']]
        )

        with self.assertRaises(Hasher.IncorrectAlgorithm):
            Hasher.set_algorithms(['blake3b', 'blake3s', 'sha513'])

        # Test hash so long :(
        Hasher.set_algorithms(['blake2s', Shake(41), 'sha3_256'])
        print(Hasher.hash('string', 'salt', 'pepper')[:64])
        self.assertEqual(
            Hasher.hash('string', 'salt', 'pepper')[:64],
            'c1caab078372d504f12703b252182dacfae760c6bad3bcefd64b639d3860a2cd'
        )

    def test_bstring_cycle(self):
        cycle = bstring_cycle(b'123')
        self.assertEqual(
            b''.join(b for (b, _) in zip(cycle, range(10))), b'1231231231')
        self.assertEqual\
            (b''.join(b for (b, _) in zip(cycle, range(10))), b'3123123123')

        cycle = bstring_cycle(b'')
        self.assertEqual(b''.join(b for (b, _) in zip(cycle, range(10))), b'')

    def test_shake(self):
        shake = Shake(32)
        self.assertEqual(
            shake(b'test').result.hexdigest(shake.length),
            'b54ff7255705a71ee2925e4a3e30e41aed489a579d5595e0df13e32e1e4dd202'
        )

        shake = Shake(8)
        self.assertEqual(
            shake(b'test').result.hexdigest(shake.length), 'b54ff7255705a71e')
        self.assertEqual(shake(b'test').digest(), b'\xb5O\xf7%W\x05\xa7\x1e')

    def test_singleton(self):
        class TestSingleton(Singleton):
            def __init__(self, attribute):
                self.attribute = attribute

        s1 = TestSingleton(10)
        s2 = TestSingleton(20)

        self.assertEqual(s1, s2)
        self.assertEqual(s1.attribute, s2.attribute)
        self.assertIs(s1, s2)
