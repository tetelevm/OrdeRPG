"""
User models, which are responsible for authorization and all of the
user's business data.
"""

from sqlalchemy import func
from server.utils.db import (
    BaseModel, StringField, DateTimeField, RandomStringField, PasswordField,
)

__all__ = ['UserModel']


class UserModel(BaseModel):
    """
    A user model that only does user authorization, but does it well.
    """

    login = StringField(string_length=50)
    pass_hash = PasswordField()
    pepper = RandomStringField(48)
    token = RandomStringField(128)
    created = DateTimeField(default=func.now())
    last_login = DateTimeField()
