"""
File with the model for inheritance in other database models. Also here is
the metaclass that generates the models.
"""

from typing import Callable
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

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
    'get_default_model_dict',
]


class DefaultInfo:
    """
    A class that contains meta-information about model.

    The name could (and would be more logical) be `Meta` instead of
    `Info`, but in this case it could be confused with the name of some
    metaclass.
    """

    tablename = None
    custom_pk = False


def get_default_model_dict() -> dict:
    """
    Translates `DefaultBaseModelFunctionality` class data into a
    dictionary and converts the dictionary to the desired form.
    """
    class DefaultBaseModelFunctionality:
        """
        A class with standard model settings.

        It could have been passed to `declarative_base`, but it was done
        that way for more convenience in generating other models.
        """

        id = IdField(name='id')
        __pydantic__ = None
        __presave_actions__ = list()
        __presetters__ = dict()

    dbmf_dict = dict(DefaultBaseModelFunctionality.__dict__)
    to_pop = ['__dict__', '__doc__', '__module__', '__weakref__']
    for key in to_pop:
        dbmf_dict.pop(key)

    dbmf_dict['__pydantic__'] = generate_pydantic_model(
        dbmf_dict, model_name='__default_model')

    return dbmf_dict


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

        dct['__pydantic__'] = generate_pydantic_model(dct)

        if hasattr(cls, '__table__'):
            if settings.database.get('type', None) == 'sqlite':
                cls.set_sqlite_arguments(cls)

    def __new__(mcs, clsname, bases, dct):
        dct = mcs.generate_dict(dct, clsname)
        cls = super().__new__(mcs, clsname, bases, dct)
        return cls

    @classmethod
    def generate_dict(mcs, dct: dict, clsname: str) -> dict:
        """
        The main method of the class. Executes all necessary logic on
        the new model class.
        """

        info = dct.get('Info', None)
        info_bases = ((info,) if info is not None else tuple()) + (DefaultInfo,)
        Info = type('Info', info_bases, {})
        dct['Info'] = Info

        dct['__tablename__'] = mcs.generate_tablename(dct['Info'], clsname)

        dbmf_dict = get_default_model_dict()
        dbmf_dict = mcs.drop_default_pk(dct['Info'], dbmf_dict)
        new_dct = dbmf_dict | dct
        for (key, value) in new_dct.items():
            dct[key] = value

        dct = mcs.set_relation_fields(clsname, dct)

        dct['__presetters__'] = mcs.create_presetters_by_decorator(dct)

        return dct

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
    def drop_default_pk(info: type, dbmf_dict: dict) -> dict:
        """
        Removes the standard `id` field from the class if custom
        `primary_key` is used.
        """

        if getattr(info, 'custom_pk', False):
            dbmf_dict.pop('id', None)
        return dbmf_dict

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
