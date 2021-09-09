"""
File with the model for inheritance in other database models. Also here is
the metaclass that generates the models.
"""

from pydantic import create_model as create_pydantic_model
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

from server.lib import ExceptionFromFormattedDoc, camel_to_snake
from .default import DefaultInfo, DefaultBaseModelFunctionality
from ..fields import FieldDefault, FieldExecutable, FieldRelationshipClass


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

    def __new__(mcs, clsname: str, bases, dct):
        dct = mcs.generate_dict(dct, clsname)
        return super(BaseModelMeta, mcs).__new__(mcs, clsname, bases, dct)

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

        dbmf_dict = mcs.get_default_model_dict()
        dbmf_dict = mcs.drop_default_pk(dct['Info'], dbmf_dict)
        dct = dbmf_dict | dct

        dct = mcs.set_relation_fields(clsname, dct)
        dct['__pydantic__'] = mcs.generate_pydantic_model(dct)

        return dct

    @staticmethod
    def get_default_model_dict() -> dict:
        """
        Translates `DefaultBaseModelFunctionality` class data into a
        dictionary and converts the dictionary to the desired form.
        """

        dbmf_dict = dict(DefaultBaseModelFunctionality.__dict__)
        dbmf_dict.pop('__dict__')
        dbmf_dict.pop('__module__')
        dbmf_dict.pop('__doc__')
        dbmf_dict.pop('__weakref__')
        return dbmf_dict

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
    def generate_pydantic_model(dct: dict) -> type:
        """Generates a `pydantic` model based on class field types."""
        # The basis of the code is taken from
        # https://github.com/tiangolo/pydantic-sqlalchemy/blob/master/pydantic_sqlalchemy/main.py

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

        return create_pydantic_model(dct['__tablename__'], **fields)

    @staticmethod
    def set_relation_fields(clsname: str, dct: dict) -> dict:
        columns = {
            name: field
            for (name, field) in dct.items()
            if isinstance(field, FieldRelationshipClass)
        }

        for (name, field) in columns.items():
            generated_fields = field.generate_fields(clsname, dct['__tablename__'])

            column_id_info = generated_fields[0]
            rel_for_c_info = generated_fields[1]
            rel_for_p_info = generated_fields[2]

            dct[name] = rel_for_c_info[1]

            column = dct.setdefault(column_id_info[0], column_id_info[1])
            if column is not column_id_info[1]:
                raise AlreadyExistsError(column_id_info[0], clsname, column)

            column = getattr(field.model_to, rel_for_p_info[0], rel_for_p_info[1])
            if column is not rel_for_p_info[1]:
                raise AlreadyExistsError(
                    column_id_info[0], field.model_to.__name__, column)
            setattr(field.model_to, rel_for_p_info[0], rel_for_p_info[1])

        return dct


ModelWorker = declarative_base(name='ModelGenerator', metaclass=BaseModelMeta)


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
