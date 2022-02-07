from types import FunctionType
from sqlalchemy.orm.decl_api import DeclarativeMeta


__all_for_module__ = [
    "attribute_presetter",
    "get_model_primary_key",
    "droppable_attribute",
    "PostInitCreator",
]
___all__ = __all_for_module__


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


def get_model_primary_key(model: DeclarativeMeta) -> type:
    return model.__table__.primary_key.columns[0]


class PostInitCreator:
    def __init__(self, call, *args, **kwargs):
        self.call = call
        self.args = args
        self.kwargs = kwargs

    def __call__(self, model_cls):
        self.call(model_cls, *self.args, **self.kwargs)
