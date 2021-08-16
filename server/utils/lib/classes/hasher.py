"""
The main data hasher, as well as a couple of additional tools for it.
"""

# import for Python 3.9-
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator, Union
from hashlib import (
    sha512,
    blake2b,
    blake2s,
    sha3_256,
    sha3_384,
    sha3_512,
    shake_256 as _shake_256
)

from ..exceptions import ExceptionFromFormattedDoc


_all_ = ['Hasher']
__all__ = _all_ + ['Shake', 'bstring_cycle', 'HashAlgAbstractType']


class HashAlgAbstractType(ABC):
    """Abstract interface for hashing algorithms."""

    @abstractmethod
    def __call__(self, byte_value: bytes) -> HashAlgAbstractType:
        """Hashes `byte_value` and saves the result."""
        pass

    @abstractmethod
    def digest(self) -> bytes:
        """Converts value from hash to `bytes` form."""
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
        """Returns `self.length` bits from the hash result."""
        return self.result.digest(self.length)


class Hasher:
    """
    A class for hashing passwords (or strings).

    This class has default algorithms, but you can set your own. Your
    algorithms can be either a string from the list of default algorithms
    or python objects with the `HashAlgAbstractType` interface.

    >>> Hasher.hash('test string')
    >>> # '18db61454a1cb54b6112dbbf37c53d7612996872bf76ed0021ff74e83a8c7c5'\
    >>> # 'cedd515d4592e18fe2f84c823813133b1854c1441ae409db65347616b29da70e8'

    >>> Hasher.hash('test string', 'test salt', 'test pepper')
    >>> # 'ffdc3337b14e35cc267a4ea21ae36f5396450299f53c8e18ef9fddaa0c48375'\
    >>> # b32bb4c799acf0563ec3974a6c43f0fca528ebb0aa31a5272decbb78641ad82cb'

    >>> Hasher.hash_algs
    >>> from hashlib import md5 as md5_as_algorithm
    >>> Hasher.set_algorithms(['blake2s', md5_as_algorithm, 'sha3_384'])
    >>> Hasher.hash_algs
    >>> # [<class '_blake2.blake2s'>, <built-in function openssl_md5>,
    >>> # <built-in function openssl_sha3_384>]
    >>> Hasher.set_algorithms()
    >>> # [<built-in function openssl_sha3_384>, <class '_blake2.blake2b'>]
    >>> Hasher.hash_algs
    >>> # [<built-in function openssl_sha3_384>, <class '_blake2.blake2b'>]
    """

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

        algorithms = [
            cls.supported_algorithms.get(algorithm, algorithm)
            for algorithm in algorithms
        ]

        try:
            for alg in algorithms:
                _ = alg(b'Testing all algorithms for errors').digest()
        except (AttributeError, TypeError) as error:
            raise cls.IncorrectAlgorithm(alg.__repr__(), ', '.join(error.args))

        cls.hash_algs = algorithms

    def __init__(self, string: str, salt: str = '', pepper: str = '', count=10 ** 5):
        self.string = bytes(string, encoding='utf-8')
        self.salt = bytes(salt, encoding='utf-8')
        self.pepper = bytes(pepper, encoding='utf-8')
        self.count = count

    @classmethod
    def hash_iter(cls, bstring: bytes) -> bytes:
        """One iteration over all algorithms."""
        for alg in cls.hash_algs:
            bstring = alg(bstring).digest()
        return bstring

    def get_hash(self) -> str:
        """Actually, the method that calculates the hash."""

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
