"""
File with the model for inheritance in other database models. Also here is
the metaclass that generates the models.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

from server.lib import ExceptionFromFormattedDoc, camel_to_snake
from ...settings import settings
from ..fields import FieldExecutable, FieldRelationshipClass
from .utils import generate_pydantic_model
from .default import DefaultInfo, get_default_model_dict


_all_ = ['BaseModel']
__all__ = _all_ + [
    'BaseModelMeta',
    'ModelWorker',
]


class AlreadyExistsError(ExceptionFromFormattedDoc):
    """<{}> field of <{}> class is already occupied (current value is <{}>)"""


class BaseModelMeta(DeclarativeMeta):
    """
    The main metaclass for generating database models.

    - injects standard info data from `DefaultInfo`
    - injects standard data from `DefaultBaseModelFunctionality`
    - creates a `pydantic` model on `__pydantic__`
    - set `__tablename__
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
