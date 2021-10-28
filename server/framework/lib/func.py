"""
Sub-module with simple functional utilities, the main requirement for
which is to be a function.
"""

import re
import os
import sys
import time
import random
import string
from pathlib import Path
from typing import Sequence, Generator, Callable


_all_ = [
    "generate_random_string",
    "generate_random_advanced_string",
    "with_randomize",
    "get_all_files_from_directory",
    "frozendict",
]
__all__ = _all_ + [
    "int_to_bytes",
    "str_to_bytes",
    "camel_to_snake",
    "default_alphabet",
    "advanced_alphabet",
    "get_all_files_from_directory_generator",
]


# ======================================================================


def int_to_bytes(i: int) -> bytes:
    """Translates an `int` type value into their `bytes` form."""
    i = abs(i)
    return i.to_bytes((i.bit_length() + 7) // 8, "big")


def str_to_bytes(data: any) -> bytes:
    """
    Converts the value to its string form, and then translates the string
    form to bytes.
    """
    return bytes(str(data), encoding="utf-8")


# ======================================================================


def with_randomize(funk):
    """
    A decorator that explicitly sets a random value to the random
    generator.
    """

    # Yes, this value is generated each time for each function.
    # Computes quickly, but allows adequate collapse of the code.
    _static_data_for_random = (
        str_to_bytes(time.time().hex())
        + int_to_bytes(id(object))
        + int_to_bytes(sys.api_version)
        + int_to_bytes(sys.hexversion)
        + str_to_bytes(os.name)
        + str_to_bytes(os.getcwd())
        + str_to_bytes(sys.executable)
        + str_to_bytes(sys.builtin_module_names)
        + int_to_bytes(os.getpid())
        + str_to_bytes(os.environ)
    )

    def randomize(*args, **kwargs):
        """
        A function that sets a (fairly absolute) random value to random
        before calling the function. After it is called, it returns
        random to the system-random value.
        """
        # Calculated each time the function is called
        random_params = (
            str_to_bytes(time.time().hex())
            + int_to_bytes(random.getrandbits(100))
            + os.urandom(100)
            + int_to_bytes(id(object()))
            + _static_data_for_random
            + str_to_bytes(time.time().hex())
        )
        random.seed(random_params)

        result = funk(*args, **kwargs)

        # Reset the seed to a system-random.
        random.seed()
        return result

    return randomize


# ======================================================================


# 62 characters
default_alphabet = string.ascii_letters + string.digits

@with_randomize
def generate_random_string(
        length: int,
        alphabet: Sequence = default_alphabet
) -> str:
    """
    Generates a random string of the desired length from the given
    alphabet.
    """
    return "".join(random.choices(alphabet, k=length))


# 94 characters
advanced_alphabet = default_alphabet + string.punctuation

def generate_random_advanced_string(length: int) -> str:
    """
    A wrapper around `generate_random_string` with a preset alphabet
    value.
    """
    return generate_random_string(length, advanced_alphabet)


# ======================================================================


pattern_before = re.compile("(.)([A-Z][a-z]+)")
pattern_after = re.compile("([a-z0-9])([A-Z])")

def camel_to_snake(name: str) -> str:
    """
    Translates NameCamelCase to name_snake_case

    >>> camel_to_snake('NameNameName')  # 'name_name_name'
    >>> camel_to_snake('name11NameName')  # 'name11_name_name'
    >>> camel_to_snake('NAMENAMENAME')  # 'namenamename'
    >>> camel_to_snake('NAMEnameNAME')  # 'nam_ename_name'
    >>> camel_to_snake('Name_name__NAME_NaMe')  # 'name_name__name__na_me'
    """

    # code from https://stackoverflow.com/a/1176023/11301238
    name = pattern_before.sub(r"\1_\2", name)
    name = pattern_after.sub(r"\1_\2", name)
    return name.lower()


# ======================================================================


def get_all_files_from_directory_generator(
        path,
        filter_func: Callable[[str], bool] = None
) -> Generator[str, None, None]:
    def get_all_files_generator():
        for (folder, _, files) in os.walk(path):
            folder = Path(folder)
            for file in files:
                yield str(folder / file)

    generator = get_all_files_generator()
    if filter_func is not None:
        generator = filter(filter_func, generator)
    return generator


def get_all_files_from_directory(
        path,
        filter_func: Callable[[str], bool] = None
) -> list[str]:
    return list(get_all_files_from_directory_generator(path, filter_func))


# ======================================================================


class frozendict(dict):
    def __setitem__(self, key, value):
        raise NotImplementedError("Cannot add or change values")

    def __delitem__(self, key):
        raise NotImplementedError("Cannot add or change values")

    def __repr__(self):
        return 'f' + super().__repr__()


# ======================================================================
