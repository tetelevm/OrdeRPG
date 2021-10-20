from sqlalchemy.sql.sqltypes import INTEGER

from server.lib import generate_random_advanced_string
from ...settings import settings
from .primitive import IntegerField, FloatField, StringField
from .field_mixins import FieldExecutable, FieldMixinMinMax


__all__ = [
    "IdField",
    "PositiveIntegerField",
    "CoefficientField",
    "PasswordField",
    "RandomStringField",
]


class IdField(IntegerField):
    """IntegerField, with arguments for primary_key."""

    if settings.database.get("type", None) == "sqlite":
        column_type = INTEGER

    _default_kwargs = {
        "autoincrement": True,
        "index": True,
        "primary_key": True,
        "unique": True,
    }


class PositiveIntegerField(IntegerField, FieldMixinMinMax):
    min_value = 0


class CoefficientField(FloatField, FieldMixinMinMax):
    """A field for storing Float type coefficients."""

    def __init__(self, min_value=0.0, max_value=1.0, *args, **kwargs):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(*args, **kwargs)


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
        return settings.password_hasher(str(password), str(salt), str(pepper))


class RandomStringField(StringField, FieldExecutable):
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

        length = kwargs.get("length", None) or self.column_type.length
        if length is None:
            raise ValueError("Length of random string is <None>!")
        return generate_random_advanced_string(length)
