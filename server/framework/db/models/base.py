"""
File with the model for inheritance in other database models. Also here is
the metaclass that generates the models.
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
    'BaseModel',
    'DefaultInfo',
]
__all__ = _all_ + [
    'BaseModelMeta',
    'ModelWorker',
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
    - creates a `__pydantic__` model
    - translates `relationship fields` to `SQLAlchemy fields`
    """

    def __init__(cls, clsname, bases, dct):
        super().__init__(clsname, bases, dct)
        cls.postinit_functionality(cls, dct)

    def __new__(mcs, clsname, bases, dct):
        dct = mcs.precreate_functionality(dct, clsname)
        return super().__new__(mcs, clsname, bases, dct)

    @classmethod
    def precreate_functionality(mcs, dct: dict, clsname: str) -> dict:
        """
        The main method of the class. Executes all necessary logic on
        the new model class.
        """

        info = dct.get('Info', None)
        info_bases = ((info,) if info is not None else tuple()) + (DefaultInfo,)
        Info = type('Info', info_bases, {})
        dct['Info'] = Info

        dct['__tablename__'] = mcs.generate_tablename(dct['Info'], clsname)
        mcs.create_default_pk(dct)

        dct = mcs.set_relation_fields(clsname, dct)

        dct['__presetters__'] = mcs.create_presetters_by_decorator(dct)
        mcs.drop_droppable_by_decorator(dct)

        return dct

    @classmethod
    def postinit_functionality(mcs, cls, dct: dict) -> None:
        cls.__pydantic__ = generate_pydantic_model(dct)

        if hasattr(cls, '__table__'):
            if settings.database.get('type', None) == 'sqlite':
                cls.set_sqlite_arguments(cls)

    @staticmethod
    def generate_tablename(info: type, clsname: str) -> str:
        """
        Generates a table name in the database based on the class name.
        You can specify your own table name.
        Warning! Changes `tablename` attribute of `Info`.

        >>> class Info: tablename = None
        >>> BaseModelMeta.generate_tablename(Info, 'YourSmthModel')
        >>> # 'your_smth'

        >>> class Info: tablename = None
        >>> BaseModelMeta.generate_tablename(Info, 'SmthWithNoModelLastWord')
        >>> # 'smth_with_no_model_last_word

        >>> class Info: tablename = 'table'
        >>> BaseModelMeta.generate_tablename(Info, 'YourSmthModel')
        >>> # 'table'
        """

        tablename = getattr(info, 'tablename', None)
        if not tablename:
            tablename = clsname.removesuffix('Model')
            tablename = camel_to_snake(tablename)
            info.tablename = tablename

        return tablename

    @staticmethod
    def create_default_pk(dct: dict) -> None:
        """
        Creates a standard `id` field as `IdField(name='id')` if
        `default_pk` is used.
        """

        if dct['Info'].default_pk:
            dct['id'] = IdField(name='id')
        if dct.get('__abstract__', False):
            dct.pop('id', None)

    @staticmethod
    def set_relation_fields(clsname: str, dct: dict) -> dict:
        columns = tuple(
            (name, field)
            for (name, field) in dct.items()
            if isinstance(field, FieldRelationshipClass)
        )

        for (name, field) in columns:
            field: FieldRelationshipClass
            field.generate_fields(clsname, name, dct)
        return dct

    @staticmethod
    def set_sqlite_arguments(cls):
        pk_col = get_model_primary_key(cls).type
        is_int_pk = isinstance(pk_col, Integer)
        if is_int_pk:
            sqlite_dict = {'autoincrement': True, 'with_rowid': True}
            cls.__table__.dialect_options["sqlite"] = sqlite_dict

    @staticmethod
    def create_presetters_by_decorator(dct: dict[str, Any]) -> dict:
        presetters = dict()
        for field_name in list(dct.keys()):
            if type(dct[field_name]) == attribute_presetter:
                presetter: attribute_presetter = dct.pop(field_name)
                presetters[presetter.to_attr] = presetter.call
        return presetters

    @staticmethod
    def drop_droppable_by_decorator(dct: dict[str, Any]) -> None:
        for field_name in list(dct.keys()):
            if type(dct[field_name]) == droppable_attribute:
                dct.pop(field_name)


ModelWorker = declarative_base(name='ModelWorker', metaclass=BaseModelMeta)


class BaseModel(ModelWorker):
    """A class for inheritance, passes the creation to its metaclass."""
    __abstract__ = True

    __pydantic__ = None
    __presave_actions__ = list()
    __presetters__ = dict()
    _m2m_models = dict()

    id = IdField(name='id')  # After creation it will delete

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
