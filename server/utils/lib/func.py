from typing import Sequence
import re
import os
import sys
import time
import random


_all_ = [
    'generate_random_string',
    'generate_random_advanced_string',
]

__all__ = _all_ + [
    'int_to_bytes',
    'str_to_bytes',
    'camel_to_snake',
]


def int_to_bytes(i: int) -> bytes:
    i = abs(i)
    return i.to_bytes((i.bit_length() + 7) // 8, 'big')


def str_to_bytes(data: any) -> bytes:
    return bytes(str(data), encoding='utf-8')


pattern_before = re.compile('(.)([A-Z][a-z]+)')
pattern_after = re.compile('([a-z0-9])([A-Z])')

def camel_to_snake(name: str) -> str:
    name = pattern_before.sub(r'\1_\2', name)
    name = pattern_after.sub(r'\1_\2', name)
    return name.lower()


default_alphabet = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
_static_data_for_random = (
    int_to_bytes(id(object)) +
    int_to_bytes(sys.api_version) +
    int_to_bytes(sys.hexversion) +
    str_to_bytes(os.name) +
    str_to_bytes(os.getcwd()) +
    str_to_bytes(sys.executable) +
    str_to_bytes(sys.builtin_module_names) +
    str_to_bytes(os.environ)
)

def generate_random_string(length: int, alphabet: Sequence = default_alphabet) -> str:
    random_params = (
        str_to_bytes(time.time().hex()) +
        int_to_bytes(random.getrandbits(50)) +
        os.urandom(50) +
        int_to_bytes(id(object())) +
        int_to_bytes(os.getpid()) +
        str_to_bytes(time.time().hex()) +
        _static_data_for_random
    )
    random.seed(random_params)
    random_string = ''.join(random.choices(alphabet, k=length))
    random.seed()
    return random_string


advanced_alphabet = default_alphabet + '`~!@#$%^&*()-_=+[{]};:\'"/?.>,<\\|'

def generate_random_advanced_string(length: int) -> str:
    return generate_random_string(length, advanced_alphabet)
