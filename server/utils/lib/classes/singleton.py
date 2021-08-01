"""
Basic implementation of the singleton pattern
"""
# The concrete implementation is taken from the first link `python singleton`

__all__ = ['Singleton']


class SingletonMeta(type):
    _instances = dict()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    pass
