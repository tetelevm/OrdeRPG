"""
File with the model for inheritance in other database models. Also here
is the metaclass that generates the models.
"""

from typing import Callable, Any
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.sql.sqltypes import Integer

from server.lib import camel_to_snake
from ...settings import settings
from ..connection.session import db_session
from ..fields import FieldExecutable, FieldRelationshipClass, IdField
from .utils import (
    generate_pydantic_model,
    attribute_presetter,
    droppable_attribute,
    get_model_primary_key,
)


_all_ = [
    "BaseModel",
    "DefaultInfo",
]
__all__ = _all_ + [
    "BaseModelMeta",
    "ModelWorker",
]


class DefaultInfo:
    """
    A class that contains meta-information about model.

    The name could (and would be more logical) be `Meta` instead of
    `Info`, but in this case it could be confused with the name of some
    metaclass.
    """

    tablename = None
    default_pk = True


class BaseModelMeta(DeclarativeMeta):
    """
    The main metaclass for generating database models.

    - set `__tablename__
    - injects standard info data from `DefaultInfo`
    - injects standard data from `DefaultBaseModelFunctionality`
    - set `__presetters__` for attributes
    - drop `droppable_attribute`s
    - creates a `__pydantic__` model
    - translates `relationship fields` to `SQLAlchemy fields`
    - executes `_postinit_actions`
    """

    base_model = None

    def __init__(cls, clsname, bases, dct):
        super().__init__(clsname, bases, dct)
        cls.postinit_functionality(cls, dct)

    def __new__(mcs, clsname, bases, dct):
        mcs.precreate_functionality(dct, clsname)
        return super().__new__(mcs, clsname, bases, dct)

    @classmethod
    def precreate_functionality(mcs, dct: dict, clsname: str):
        """
        The main method of the class. Executes all necessary logic on
        the new model class.
        """

        mcs.set_changeable_clsattr(dct)
        mcs.add_info(dct)
        mcs.generate_tablename(dct, clsname)
        mcs.create_default_pk(dct)
        mcs.set_relation_fields(clsname, dct)
        mcs.create_presetters_by_decorator(dct)
        mcs.drop_droppable_by_decorator(dct)

    @classmethod
    def postinit_functionality(mcs, cls, dct: dict):
        cls.__pydantic__ = generate_pydantic_model(dct)

        if hasattr(cls, "__table__"):
            if settings.database.get("type", None) == "sqlite":
                cls.set_sqlite_arguments(cls)

        for action in cls._postinit_actions:
            action: Callable
            action(cls)
        del cls._postinit_actions

    @classmethod
    def set_changeable_clsattr(mcs, dct: dict):
        dct.setdefault("_postinit_actions", [])

        if mcs.base_model is not None:
            list_of_changeable = [
                "__presave_actions__",
                "__presetters__",
                "_m2m_models",
            ]
            for attr in list_of_changeable:
                dct[attr] = mcs.base_model.__annotations__[attr]()

    @staticmethod
    def add_info(dct):
        info = dct.get("Info", None)
        info_bases = ((info,) if info is not None else tuple()) + (DefaultInfo,)
        Info = type("Info", info_bases, {})
        dct["Info"] = Info

    @staticmethod
    def generate_tablename(dct: dict, clsname: str):
        """
        Generates a table name in the database based on the class name.
        You can specify your own table name.
        Warning! Changes `tablename` attribute of `Info`.
        """

        info = dct["Info"]
        tablename = getattr(info, "tablename", None)

        if not tablename:
            tablename = dct.pop("__tablename__", None)

        if not tablename:
            tablename = clsname.removesuffix("Model")
            tablename = camel_to_snake(tablename)

        dct["__tablename__"] = tablename
        info.tablename = tablename

    @staticmethod
    def create_default_pk(dct: dict):
        """
        Creates a standard `id` field as `IdField(name='id')` if
        `default_pk` is used.
        """

        if dct["Info"].default_pk:
            dct["id"] = IdField(name="id")
        if dct.get("__abstract__", False):
            dct.pop("id", None)

    @staticmethod
    def set_relation_fields(clsname: str, dct: dict):
        columns = tuple(
            (name, field)
            for (name, field) in dct.items()
            if isinstance(field, FieldRelationshipClass)
        )

        for (name, field) in columns:
            field: FieldRelationshipClass
            field.generate_fields(clsname, name, dct)

    @staticmethod
    def set_sqlite_arguments(cls):
        pk = get_model_primary_key(cls)
        is_int_pk = isinstance(pk.type, Integer)
        is_increment = pk.autoincrement

        if is_int_pk and is_increment:
            sqlite_dict = {"autoincrement": True, "with_rowid": True}
            cls.__table__.dialect_options["sqlite"] = sqlite_dict

    @staticmethod
    def create_presetters_by_decorator(dct: dict[str, Any]):
        presetters = dict()
        for field_name in list(dct.keys()):
            if type(dct[field_name]) == attribute_presetter:
                presetter: attribute_presetter = dct.pop(field_name)
                presetters[presetter.to_attr] = presetter.call

        dct["__presetters__"] = presetters

    @staticmethod
    def drop_droppable_by_decorator(dct: dict[str, Any]):
        for field_name in list(dct.keys()):
            if type(dct[field_name]) == droppable_attribute:
                dct.pop(field_name)


ModelWorker = declarative_base(name="ModelWorker", metaclass=BaseModelMeta)


def _add_base_model_into_base_model_meta(base_model):
    BaseModelMeta.base_model = base_model


class BaseModel(ModelWorker):
    """A class for inheritance, passes the creation to its metaclass."""

    __abstract__ = True
    _postinit_actions = [_add_base_model_into_base_model_meta]  # drop after create

    __pydantic__ = None
    __presave_actions__: list = list()
    __presetters__: dict = dict()
    _m2m_models: dict = dict()

    id = IdField(name="id")  # after creation it will delete

    def __init__(self, *args, **kwargs):
        for (name, field_class) in self.__table__.columns.items():
            if isinstance(field_class, FieldExecutable):
                if name in kwargs.keys():
                    kwargs[name] = field_class.execute(kwargs[name])
                elif not field_class.need_argument:
                    kwargs[name] = field_class.execute()

        super().__init__(*args, **kwargs)

    def save(self):
        for action_name in self.__presave_actions__:
            action: Callable = getattr(self, action_name)
            action()
        db_session.add(self)
        db_session.commit()

    def __setattr__(self, key, value):
        if key in self.__presetters__:
            value = self.__presetters__[key](self, value)
        super().__setattr__(key, value)
