from abc import ABC

from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.visitors import TraversibleType
from sqlalchemy.sql.sqltypes import BigInteger
from sqlalchemy.orm import relationship, backref

from .base import FieldDefault


__all__ = [
    'FieldRelationship',
    'ForeignKeyCustomTypeField',
    'ForeignKeyField',
]


class FieldRelationship(ABC):
    pass


class ForeignKeyCustomTypeField(FieldDefault, FieldRelationship):
    column_type = TraversibleType


    def __init__(self, *args, **kwargs):
        if 'key_type' in kwargs:
            self.column_type = kwargs.pop('key_type')
        super().__init__(*args, **kwargs)


class ForeignKeyField(ForeignKeyCustomTypeField):
    column_type = BigInteger

    def __init__(self, *args, **kwargs):
        if 'key_type' in kwargs:
            self.column_type = kwargs.pop('key_type')
        super().__init__(*args, **kwargs)
