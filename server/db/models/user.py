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
    OnoToOneField,
)

__all__ = ['UserModel', 'PersonModel']


class UserModel(BaseModel):
    """
    A user model that only does user authorization, but does it well.
    """

    login = StringField(50, nullable=False)
    pass_hash = PasswordField()
    pepper = RandomStringField(48)
    token = RandomStringField(128)
    created = DateTimeField(default=func.now())
    last_login = DateTimeField()
    is_deleted = BooleanField(default=False, nullable=False)


class PersonModel(BaseModel):
    """A user model containing business logic."""

    type = IntegerField(nullable=False)
    user = OnoToOneField(UserModel)
    level = IntegerField(default=1, nullable=False)
    experience = IntegerField(default=0, nullable=False)
    money = IntegerField(default=0, nullable=False)
    rating = IntegerField(default=0, nullable=False)
    kill_ratio = CoefficientField(default=0., nullable=False)
    fights_count = PositiveIntegerField(default=0, nullable=False)
