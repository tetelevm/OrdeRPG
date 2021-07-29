from server.utils.db import (
    BaseModel, StringField, DateTimeField, RandomStringField, PasswordField,
)

__all__ = ['UserModel']


class UserModel(BaseModel):
    login = StringField(string_length=50)
    pass_hash = PasswordField()
    pepper = RandomStringField(48)
    token = RandomStringField(128)
    last_login = DateTimeField()
