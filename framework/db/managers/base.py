from types import NoneType

from sqlalchemy.orm import DeclarativeMeta

from ..utils.func import generate_pydantic_model


__all_for_module__ = ["BasePeel"]
__all__ = __all_for_module__ + ["BasePeelMeta"]


class BasePeelMeta(type):
    def __new__(mcs, clsname, bases, dct):
        dct.setdefault("__abstract__", False)
        if dct["__abstract__"]:
            return super().__new__(mcs, clsname, bases, dct)

        model_cls = dct.get("Model", None)
        if model_cls is None:
            raise AttributeError("No model class")
        elif not isinstance(model_cls, DeclarativeMeta):
            raise AttributeError("The model must be a descendant of BaseModel.")

        dct["__pydantic__"] = generate_pydantic_model(model_cls)
        dct["_m_attr_list"] = [str(field.name) for field in model_cls.__table__.columns]

        cls = super().__new__(mcs, clsname, bases, dct)
        return cls


class BasePeel(metaclass=BasePeelMeta):
    __abstract__ = True

    Model: type = NoneType  # BaseModelMeta
    model: object = None
    _m_attr_list: list[str] = []
    __pydantic__ = dict()

    def __setattr__(self, key, value):
        if self.model is None:
            raise AttributeError("The model object is not initialized")
        if key in self._m_attr_list:
            setattr(self.model, key, value)
        else:
            raise AttributeError(
                f"{self.Model.__name__} model has no {key} attribute")

    def __init__(self):
        super().__setattr__("model", self.Model())
