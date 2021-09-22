from types import FunctionType, LambdaType
from pydantic import create_model as create_pydantic_model
from ..fields import FieldDefault


__all__ = [
    'generate_pydantic_model',
    'attribute_presetter',
]


def generate_pydantic_model(dct: dict, model_name: str = None) -> type:
    """Generates a `pydantic` model based on class field types."""
    # The basis of the code is taken from
    # https://github.com/tiangolo/pydantic-sqlalchemy/blob/master/pydantic_sqlalchemy/main.py

    model_name = model_name or dct['__tablename__']

    columns = {
        name: field
        for (name, field) in dct.items()
        if isinstance(field, FieldDefault)
    }

    fields = dict()
    for (name, field) in columns.items():
        default = None
        if field.default is None and not field.nullable:
            default = ...

        fields[name] = (field.type.python_type, default)
    return create_pydantic_model(model_name, **fields)


def _is_attribute_presetter(attr):
    is_func = isinstance(attr, (FunctionType, LambdaType))
    has_link = hasattr(attr, 'to_attr')
    return is_func and has_link


def attribute_presetter(name):
    def attribute_presetter_marker(func):
        func.to_attr = name
        return func
    return attribute_presetter_marker


attribute_presetter.is_presetter = _is_attribute_presetter
