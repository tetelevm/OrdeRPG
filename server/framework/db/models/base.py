"""
File with the model for inheritance in other database models. Also here is
the metaclass that generates the models.
"""

from typing import Callable
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.sql.sqltypes import Integer

from server.lib import ExceptionFromFormattedDoc, camel_to_snake
from ...settings import settings
from ..connection.session import db_session
from ..fields import FieldExecutable, FieldRelationshipClass, IdField
from .utils import generate_pydantic_model, attribute_presetter


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


class AlreadyExistsError(ExceptionFromFormattedDoc):
    """<{}> field of <{}> class is already occupied (current value is <{}>)"""


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
        if  dct.get('__abstract__', False):
            dct.pop('id', None)

    @staticmethod
    def set_relation_fields(clsname: str, dct: dict) -> dict:
        columns = {
            name: field
            for (name, field) in dct.items()
            if isinstance(field, FieldRelationshipClass)
        }

        for (name, field) in columns.items():
            field: FieldRelationshipClass

            rel_for_c_info = field.generate_rel_for_c(dct['__tablename__'])
            dct[name] = rel_for_c_info[1]

            column_id_info = field.generate_id_column()
            column = dct.setdefault(column_id_info[0], column_id_info[1])
            if column is not column_id_info[1]:
                raise AlreadyExistsError(column_id_info[0], clsname, column)

            rel_for_p_info = field.generate_rel_for_p(dct['__tablename__'], clsname)
            column = getattr(field.model_to, rel_for_p_info[0], rel_for_p_info[1])
            if column is not rel_for_p_info[1]:
                raise AlreadyExistsError(
                    column_id_info[0], field.model_to.__name__, column)
            setattr(field.model_to, rel_for_p_info[0], rel_for_p_info[1])

        return dct

    @staticmethod
    def set_sqlite_arguments(cls):
        pk_col = cls.__table__.primary_key.columns[0].type
        is_int_pk = isinstance(pk_col, Integer)
        if is_int_pk:
            sqlite_dict = {'autoincrement': True, 'with_rowid': True}
            cls.__table__.dialect_options["sqlite"] = sqlite_dict

    @staticmethod
    def create_presetters_by_decorator(dct: dict) -> dict:
        presetters_list = [
            (name, attr)
            for (name, attr) in dct.items()
            if attribute_presetter.is_presetter(attr)
        ]
        presetters = {
            presetter.to_attr: dct.pop(attr_name)
            for (attr_name, presetter) in presetters_list
        }
        return presetters


ModelWorker = declarative_base(name='ModelWorker', metaclass=BaseModelMeta)


class BaseModel(ModelWorker):
    """A class for inheritance, passes the creation to its metaclass."""
    __abstract__ = True

    __pydantic__ = None
    __presave_actions__ = list()
    __presetters__ = dict()

    id = None  # After creation it will have value of `IdField(name='id')`

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

    def __setattr__(self, key, value):
        if key in self.__presetters__:
            value = self.__presetters__[key](self, value)
        super().__setattr__(key, value)
