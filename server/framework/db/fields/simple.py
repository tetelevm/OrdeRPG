from sqlalchemy.sql.sqltypes import BigInteger, Float, String, DateTime

from server.lib import generate_random_advanced_string
from ...settings import settings
from .default import FieldDefault, FieldExecutableInterface


__all__ = [
    'IntegerField',
    'IdField',
    'FloatField',
    'CoefficientField',
    'StringField',
    'PasswordField',
    'RandomStringField',
    'DateTimeField',
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


class IdField(IntegerField):
    """IntegerField, with arguments for primary_key."""

    _default_kwargs = {
        'autoincrement': True,
        'index': True,
        'primary_key': True,
        'unique': True,
    }


class FloatField(FieldDefault):
    """Standard field of type Float."""
    column_type = Float


class CoefficientField(FloatField, FieldExecutableInterface):
    """A field for storing Float type coefficients."""

    def __init__(self, min_value=0., max_value=1., *args, **kwargs):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(*args, **kwargs)

    def execute(self, *args, **kwargs):
        value = kwargs.get('value', 0)
        return min(self.max_value, max(value, self.min_value))


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


class PasswordField(StringField):
    """
    A field for storing a password value, which differs from a simple
    string by its ability to hash values.
    """

    @staticmethod
    def generate(password, salt, pepper):
        """
        Hashes the values passed to it using the hashing algorithm set
        in `settings` object.
        """
        return settings.password_hasher(password, salt, pepper)


class RandomStringField(StringField, FieldExecutableInterface):
    """
    Standard string field, but with the ability to generate a random
    value.
    """

    need_argument = False

    def execute(self, *args, **kwargs) -> str:
        """
        Generates a random string of alphabet [a-zA-Z + `special symbols`].

        If this field is of limited length, by default the generated
        string will be of this length, otherwise you must specify the
        desired length.
        """

        length = kwargs.get('length', None) or self.column_type.length
        if length is None:
            raise ValueError('Length of random string is <None>!')
        return generate_random_advanced_string(length)


class DateTimeField(FieldDefault):
    """Standard field with DateTime type."""
    column_type = DateTime
