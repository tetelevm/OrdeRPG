"""
User models, which are responsible for authorization and all of the
user's business data.
"""

from sqlalchemy import func
from framework.db.models import (
    attribute_presetter,
    BaseModel,
)
from framework.db.fields import (
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
from server.settings import settings


__all__ = ["UserModel", "PersonModel"]


class UserModel(BaseModel):
    """
    A user model that only does user authorization, but does it well.
    """

    login = StringField(50, nullable=False)
    name = StringField(50, nullable=False)
    password = PasswordField(nullable=False)
    pepper = RandomStringField(48)
    token = RandomStringField(128)
    created = DateTimeField(default=func.now())
    last_login = DateTimeField()
    is_deleted = BooleanField(default=False, nullable=False)

    @attribute_presetter("password")
    def password_setter(self, value):
        return self.generate_password(value)

    def generate_password(self, password):
        return UserModel.password.generate(
            password,
            self.pepper,
            settings.hash_salt
        )


class PersonModel(BaseModel):
    """A user model containing business logic."""

    user = OnoToOneField(UserModel)
    type = IntegerField(nullable=False)
    level = IntegerField(default=1, nullable=False)
    experience = IntegerField(default=0, nullable=False)
    money = IntegerField(default=0, nullable=False)
    rating = IntegerField(default=0, nullable=False)
    kill_ratio = CoefficientField(default=0.0, nullable=False)
    fights_count = PositiveIntegerField(default=0, nullable=False)
