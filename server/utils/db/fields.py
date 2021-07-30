from abc import ABC, ABCMeta

from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql.visitors import TraversibleType

from ..lib import generate_random_advanced_string
from ..settings import settings


_all_ = [
    'IntegerField',
    'IdField',
    'StringField',
    'PasswordField',
    'RandomStringField',
    'DateTimeField',
]

__all__ = [
    'FieldDefaultMeta',
    'FieldDefault',
] + _all_


class FieldAutoGenerated:
    @staticmethod
    def generate(*args, **kwargs):
        pass


class FieldDefaultMeta(ABCMeta, TraversibleType):
    def __new__(mcs, clsname, bases, dct):
        clsname, bases, dct = mcs.__pre_construct_field(clsname, bases, dct)
        return super(FieldDefaultMeta, mcs).__new__(mcs, clsname, bases + (Column, ABC), dct)

    @staticmethod
    def __pre_construct_field(clsname, bases, dct):
        # Create and inheritance `_default_kwargs`
        cls_default_kwargs = dct.get('_default_kwargs', dict())
        parent_default_kwargs = {
            key: val
            for cls in bases
            for (key, val) in getattr(cls, '_default_kwargs', dict()).items()
        }
        dct['_default_kwargs'] = parent_default_kwargs | cls_default_kwargs

        return clsname, bases, dct


class FieldDefault(metaclass=FieldDefaultMeta):
    type = None
    _default_kwargs = dict()

    def __init__(self, **kwargs):
        kwargs = self._default_kwargs | kwargs
        super(FieldDefault, self).__init__(self.type, **kwargs)


class IntegerField(FieldDefault):
    type = BigInteger


class IdField(IntegerField):
    _default_kwargs = {
        'autoincrement': True,
        'index': True,
        'nullable': False,
        'primary_key': True,
        'unique': True,
    }


class StringField(FieldDefault):
    type = String

    def __init__(self, string_length=None, **kwargs):
        self.type = self.type(length=string_length)
        super(StringField, self).__init__(**kwargs)


class PasswordField(StringField, FieldAutoGenerated):
    @staticmethod
    def generate(password, salt, pepper):
        return settings.password_hasher(password, salt, pepper)


class RandomStringField(StringField, FieldAutoGenerated):
    def generate(self, length: int = None) -> str:
        length = length or self.type.length
        if length is None:
            raise ValueError('Length of random string is <None>!')
        return generate_random_advanced_string(length)


class DateTimeField(FieldDefault):
    type = DateTime
