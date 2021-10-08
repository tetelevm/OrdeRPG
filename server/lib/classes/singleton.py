"""
Basic implementation of the singleton pattern
"""

_all_ = ['Singleton']
__all__ = _all_ + ['SingletonMeta']


class SingletonMeta(type):
    """
    Standard singleton implementation via a metaclass.

    `instances` keeps references to created objects of all singe-classes.
    """

    instances = dict()

    def __call__(cls, *args, **kwargs):
        if cls not in cls.instances:
            cls.instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls.instances[cls]


class Singleton(metaclass=SingletonMeta):
    """A class for inheritance that calls SingletonMeta metaclass constructor."""
    pass
