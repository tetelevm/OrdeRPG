from framework.db import BaseModel
from framework.db.fields import (
    IdField,
    IntegerField,
    FloatField,
    StringField,
    ForeignKeyField,
    ManyToManyField,
)
from framework.db.fields.relations import ManyToManyColumn

from .location import ShopModel
from .fight import CharacteristicModel


__all__ = ["ItemTypeModel", "CharacteristicItemModel", "ItemModel"]


class ItemTypeModel(BaseModel):
    name = StringField(20, nullable=False)


class CharacteristicItemModel(BaseModel):
    id = IdField(autoincrement=False)
    value = FloatField(nullable=False)
    item_id = ManyToManyColumn(
        IdField.column_type,
        'item.id',
        primary_key=True,
    )
    characteristic_token = ManyToManyColumn(
        StringField.column_type,
        'characteristic.token',
        primary_key=True,
    )

    class Info:
        default_pk = False


class ItemModel(BaseModel):
    type = ForeignKeyField(ItemTypeModel)
    name = StringField(40, nullable=False)
    description = StringField()
    characteristics = ManyToManyField(
        CharacteristicModel,
        backref="items",
        through=CharacteristicItemModel,
    )
    shops = ManyToManyField(ShopModel)
    min_level = IntegerField(default=0)
