from types import FunctionType
from pydantic import create_model as create_pydantic_model
from ..fields.base import FieldDefault


__all__ = [
    'generate_pydantic_model',
    'attribute_presetter',
    'get_model_primary_key',
    'droppable_attribute',
]


def generate_pydantic_model(dct: dict, model_name: str = None) -> type:
    """Generates a `pydantic` model based on class field types."""
    # The basis of the code is taken from
    # https://github.com/tiangolo/pydantic-sqlalchemy/blob/master/pydantic_sqlalchemy/main.py

    model_name = model_name or dct['__tablename__']

    columns = (
        (name, field)
        for (name, field) in dct.items()
        if isinstance(field, FieldDefault)
    )

    fields = dict()
    for (name, field) in columns:
        default = None
        if field.default is None and not field.nullable:
            default = ...

        fields[name] = (field.type.python_type, default)
    return create_pydantic_model(model_name, **fields)


class attribute_presetter:
    to_attr: str = None
    call: FunctionType = None

    def __new__(cls, name: str, link: FunctionType = None):
        self = super().__new__(cls)
        self.to_attr = name
        if link is not None:
            self = self(link)
        return self

    def __call__(self, func: FunctionType):
        self.call = func
        return self


class droppable_attribute:
    def __init__(self, attr):
        self.value = attr


def get_model_primary_key(model):
    return model.__table__.primary_key.columns[0]
