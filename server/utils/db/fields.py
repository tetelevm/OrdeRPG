from abc import ABC, ABCMeta

from sqlalchemy import Column, BigInteger
from sqlalchemy.sql.visitors import TraversibleType


__all__ = [
    'FieldDefault',
    'IdField',
]


class FieldDefaultMeta(ABCMeta, TraversibleType):
    def __new__(mcs, clsname, bases, dct):
        return super(FieldDefaultMeta, mcs).__new__(mcs, clsname, bases + (Column, ABC), dct)


class FieldDefault(metaclass=FieldDefaultMeta):
    pass


class IdField(FieldDefault):
    pynotation = int

    def __init__(self):
        super(IdField, self).__init__(
            BigInteger,
            autoincrement=True,
            index=True,
            nullable=False,
            primary_key=True,
            unique=True,
        )
