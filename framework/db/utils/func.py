from sqlalchemy.orm.decl_api import DeclarativeMeta
from pydantic import create_model as create_pydantic_model


__all_for_module__ = [
    "generate_pydantic_model",
]
___all__ = __all_for_module__


def generate_pydantic_model(model: DeclarativeMeta) -> type:
    """Generates a `pydantic` model based on class field types."""
    # The basis of the code is taken from
    # https://github.com/tiangolo/pydantic-sqlalchemy/blob/master/pydantic_sqlalchemy/main.py

    model_name = getattr(model, "__tablename__", "")
    fields = dict()
    for field in model.__table__.columns:
        default = None
        if field.default is None and not field.nullable:
            default = ...
        fields[str(field.name)] = (field.type.python_type, default)
    return create_pydantic_model(model_name, **fields)
