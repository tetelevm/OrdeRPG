from server.utils.db import BaseModel, StringField, DateTimeField
from server.settings import settings


__all__ = ['UserModel']


class UserModel(BaseModel):
    login = StringField(string_length=50)
    pass_hash = StringField()
    pepper = StringField(48)
    token = StringField(128)
    last_login = DateTimeField()

    @staticmethod
    def hash_password(password, salt, pepper):
        return settings.password_hasher(password, salt, pepper)
