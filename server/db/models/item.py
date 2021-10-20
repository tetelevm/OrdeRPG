from server.framework.db import BaseModel
from server.framework.db.fields import (
    IntegerField,
    StringField,
    ForeignKeyField,
    ManyToManyField,
)
from .location import ShopModel
from .fight import CharacteristicModel


__all__ = ["ItemTypeModel", "ItemModel"]


class ItemTypeModel(BaseModel):
    name = StringField(20, nullable=False)


class ItemModel(BaseModel):
    type = ForeignKeyField(ItemTypeModel)
    name = StringField(40, nullable=False)
    description = StringField()
    characteristics = ManyToManyField(CharacteristicModel, backref="items")
    shops = ManyToManyField(ShopModel)
    min_level = IntegerField(default=0)
