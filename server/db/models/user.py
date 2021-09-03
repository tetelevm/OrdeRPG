"""
User models, which are responsible for authorization and all of the
user's business data.
"""

from sqlalchemy import func
from server.framework.db import (
    BaseModel,
    IntegerField,
    StringField,
    DateTimeField,
    RandomStringField,
    PasswordField,
    CoefficientField,
    BooleanField,
    PositiveIntegerField,
    ForeignKeyField,
)

__all__ = ['UserModel', 'PersonModel']


class UserModel(BaseModel):
    """
    A user model that only does user authorization, but does it well.
    """

    login = StringField(50)
    pass_hash = PasswordField()
    pepper = RandomStringField(48)
    token = RandomStringField(128)
    created = DateTimeField(default=func.now())
    last_login = DateTimeField()
    is_deleted = BooleanField()


class PersonModel(BaseModel):
    """A user model containing business logic."""

    type = IntegerField()
    user = ForeignKeyField(UserModel)
    level = IntegerField()
    experience = IntegerField()
    money = IntegerField()
    rating = IntegerField()
    kill_ratio = CoefficientField()
    fights_count = PositiveIntegerField()
