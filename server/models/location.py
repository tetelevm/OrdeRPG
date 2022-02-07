from framework.db.models import BaseModel
from framework.db.fields import (
    StringField,
    OnoToOneField,
    CoefficientField,
)


__all__ = ["LocationModel", "ShopModel"]


class LocationModel(BaseModel):
    name = StringField(40, nullable=False)
    description = StringField(default='', nullable=False)


class ShopModel(BaseModel):
    location = OnoToOneField(LocationModel)
    sales_ratio = CoefficientField(3.0, 7.0, default=5.0, nullable=False)
    rebate = CoefficientField(0.5, 1.5, default=1.0, nullable=False)
