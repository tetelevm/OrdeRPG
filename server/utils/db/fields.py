from abc import ABC, ABCMeta
from datetime import datetime as datime

from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql.visitors import TraversibleType


_all_ = [
    'IntegerField',
    'IdField',
    'StringField',
    'DateTimeField',
]

__all__ = [
    'FieldDefaultMeta',
    'FieldDefault',
] + _all_


class FieldDefaultMeta(ABCMeta, TraversibleType):
    def __new__(mcs, clsname, bases, dct):
        cls_default_kwargs = dct.get('_default_kwargs', dict())
        parent_default_kwargs = {
            key: val
            for cls in bases
            for (key, val) in cls._default_kwargs.items()
        }
        dct['_default_kwargs'] = parent_default_kwargs | cls_default_kwargs
        return super(FieldDefaultMeta, mcs).__new__(mcs, clsname, bases + (Column, ABC), dct)


class FieldDefault(metaclass=FieldDefaultMeta):
    pynotation = None
    _field_type = None
    _default_kwargs = dict()

    def __init__(self, **kwargs):
        kwargs = self._default_kwargs | kwargs
        super(FieldDefault, self).__init__(self._field_type, **kwargs)


class IntegerField(FieldDefault):
    pynotation = int
    _field_type = BigInteger


class IdField(IntegerField):
    _default_kwargs = {
        'autoincrement': True,
        'index': True,
        'nullable': False,
        'primary_key': True,
        'unique': True,
    }


class StringField(FieldDefault):
    pynotation = str
    _field_type = String

    def __init__(self, string_length=None, **kwargs):
        self._field_type = self._field_type(length=string_length)
        super(StringField, self).__init__(**kwargs)


class DateTimeField(FieldDefault):
    pynotation = datime
    _field_type = DateTime
