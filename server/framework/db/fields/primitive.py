from sqlalchemy.sql.sqltypes import BigInteger, Float, String, DateTime, Boolean

from .base import FieldDefault


__all__ = [
    "IntegerField",
    "FloatField",
    "StringField",
    "DateTimeField",
    "BooleanField",
]


class IntegerField(FieldDefault):
    """
    Standard field of type Integer.

    The field type is a BigInteger out of consideration that in today's
    databases a few bytes do not play a particularly big role, but it
    saves programmers from overflow problems that were unexpected at the
    beginning of development.
    """

    column_type = BigInteger


class FloatField(FieldDefault):
    """Standard field of type Float."""

    column_type = Float


class StringField(FieldDefault):
    """
    Standard field with type String.

    The default is unlimited length, otherwise the length must be
    specified in `kwargs`.
    """

    column_type = String

    def __init__(self, string_length=None, **kwargs):
        self.column_type = self.column_type(length=string_length)
        super().__init__(**kwargs)


class DateTimeField(FieldDefault):
    """Standard field with DateTime type."""

    column_type = DateTime


class BooleanField(FieldDefault):
    """Standard field with Boolean type."""

    column_type = Boolean
