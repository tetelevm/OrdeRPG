from server.framework.db import BaseModel
from server.framework.db.fields import (
    StringField,
    OnoToOneField,
)


__all__ = ["LocationModel", "ShopModel"]


class LocationModel(BaseModel):
    name = StringField(40, nullable=False)
    description = StringField()


class ShopModel(BaseModel):
    location = OnoToOneField(LocationModel)
