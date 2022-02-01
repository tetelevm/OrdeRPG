from framework.db import BaseModel
from framework.db.fields import (
    StringField,
)


__all__ = ["CharacteristicModel"]


class CharacteristicModel(BaseModel):
    token = StringField(40, primary_key=True, nullable=False, index=True)
    name = StringField(40, nullable=False)

    class Info:
        default_pk = False
