"""
The main data hasher, as well as a couple of additional tools for it.
"""

# import for Python 3.9-
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator, Union
from hashlib import sha512, blake2b, blake2s, sha3_256, sha3_384, sha3_512
from hashlib import shake_256 as _shake_256

from ..exceptions import ExceptionFromFormattedDoc


_all_ = ['Hasher']
__all__ = _all_ + ['Shake', 'bstring_cycle']


class HashAlgAbstractType(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs) -> HashAlgAbstractType:
        pass

    @abstractmethod
    def digest(self) -> bytes:
        pass


def bstring_cycle(bstring: bytes) -> Iterator[bytes]:
    """
    Standard `itertools.cycle`, but for `bytes` and with the ability to
    pass an empty value.
    """

    while bstring == b'':
        yield b''
    while True:
        for index in range(len(bstring)):
            yield bstring[index:index+1]


class Shake(HashAlgAbstractType):
    """
    A custom implementation of the standard `shake_256`.
    Made to call the `.digest()` method without specifying length.
    """

    result = _shake_256()

    def __init__(self, length: int = 32):
        self.length = length

    def __call__(self, *args, **kwargs) -> Shake:
        self.result = _shake_256(*args, **kwargs)
        return self

    def digest(self) -> bytes:
        return self.result.digest(self.length)


class Hasher:
    # Error when algorithm validity test fails
    class IncorrectAlgorithm(ExceptionFromFormattedDoc):
        """{} algorithm: {}"""

    supported_algorithms = {
        'blake2b': blake2b,
        'blake2s': blake2s,
        'sha512': sha512,
        'sha3_256': sha3_256,
        'sha3_384': sha3_384,
        'sha3_512': sha3_512,
        'shake256': Shake(32),
        'shake384': Shake(48),
        'shake512': Shake(64),
    }
    hash_algs = [sha3_384, blake2b]

    @classmethod
    def set_algorithms(cls, algorithms: list[Union[str, HashAlgAbstractType]] = None):
        """
        A method to set up and test the validity of hashing algorithms.

        This is done so that you can keep secret not only the
        salt/pepper, but also the hashing algorithms.
        """
        if algorithms is None:
            algorithms = ['sha3_384', 'blake2b']

        cls.hash_algs = [
            cls.supported_algorithms.get(algorithm, algorithm)
            for algorithm in algorithms
        ]

        try:
            for alg in cls.hash_algs:
                _ = alg(b'Testing all algorithms for errors').digest()
        except (AttributeError, TypeError) as error:
            raise cls.IncorrectAlgorithm(alg.__repr__(), ', '.join(error.args))

    def __init__(self, string: str, salt: str = '', pepper: str = '', count=10 ** 5):
        self.string = bytes(string, encoding='utf-8')
        self.salt = bytes(salt, encoding='utf-8')
        self.pepper = bytes(pepper, encoding='utf-8')
        self.count = count

    @classmethod
    def hash_iter(cls, bstring: bytes) -> bytes:
        """ One iteration over all algorithms. """
        for alg in cls.hash_algs:
            bstring = alg(bstring).digest()
        return bstring

    def get_hash(self) -> str:
        """ Actually, the method that calculates the hash. """

        # Reduces the number of hashing algorithm calls from
        # `count * len(hash_algs)` to ~= `count`
        range_count = range(self.count // len(self.hash_algs))

        cycle_salt = bstring_cycle(self.salt)
        cycle_pepper = bstring_cycle(self.pepper)

        for (_, p, s) in zip(range_count, cycle_salt, cycle_pepper):
            self.string = p + self.string + s
            self.string = self.hash_iter(self.string)

        return self.string.hex()

    @classmethod
    def hash(cls, string: str, salt: str = '', pepper: str = '') -> str:
        """
        A method for configuring the project to briefly call the data
        hashing.
        """
        return cls(string, salt, pepper).get_hash()
