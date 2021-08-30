"""
File with the model for inheritance in other database models. Also here is
the metaclass that generates the models.
"""

from pydantic import create_model as create_pydantic_model
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

from server.lib import camel_to_snake
from .default import DefaultInfo, DefaultBaseModelFunctionality
from ..fields import FieldDefault, FieldExecutableInterface


_all_ = ['BaseModel']
__all__ = _all_ + [
    'BaseModelMeta',
    'ModelWorker',
]


ModelWorker = declarative_base(name='ModelGenerator')


class BaseModelMeta(DeclarativeMeta):
    """
    The main metaclass for generating database models.

    - injects standard data from `DefaultBaseModelFunctionality`
    - creates a `pydantic` model on `__pydantic__`
    - set `__tablename__
    """

    def __new__(mcs, clsname, bases, dct):
        dct = mcs.generate_dict(dct, clsname)
        return super(BaseModelMeta, mcs).__new__(mcs, clsname, bases, dct)

    @classmethod
    def generate_dict(mcs, dct: dict, clsname: str) -> dict:
        """
        The main method of the class. Executes all necessary logic on
        the new model class.
        """

        dbmf_dict = BaseModelMeta.get_default_model_dict()
        info = dct.get('Info', DefaultInfo)

        dct['__tablename__'] = mcs._generate_tablename(info, clsname)

        dbmf_dict = mcs._drop_default_pk(info, dbmf_dict)
        dct = dbmf_dict | dct

        dct['__pydantic__'] = mcs._generate_pydantic_model(dct)

        return dct

    @staticmethod
    def get_default_model_dict() -> dict:
        """
        Translates `DefaultBaseModelFunctionality` class data into a
        dictionary and converts the dictionary to the desired form.
        """

        dbmf_dict = dict(DefaultBaseModelFunctionality.__dict__)
        dbmf_dict.pop('__dict__')
        dbmf_dict.pop('__weakref__')
        return dbmf_dict

    @staticmethod
    def _generate_tablename(info: type, clsname: str) -> str:
        """
        Generates a table name in the database based on the class name.
        You can specify your own table name.

        >>> BaseModelMeta._generate_tablename(..., 'YourSmthModel')
        >>> # 'your_smth'
        >>> BaseModelMeta._generate_tablename(..., 'SmthWithNoModelLastWord')
        >>> # 'smth_with_no_model_last_word'
        """

        tablename = getattr(info, 'tablename', None)
        if not tablename:
            tablename = clsname.removesuffix('Model')
            tablename = camel_to_snake(tablename)
        return tablename

    @staticmethod
    def _drop_default_pk(info: type, dbmf_dict: dict) -> dict:
        """
        Removes the standard `id` field from the class if custom
        `primary_key` is used.
        """

        if getattr(info, 'custom_pk', False):
            dbmf_dict.pop('id', None)
        return dbmf_dict

    @staticmethod
    def _generate_pydantic_model(dct: dict) -> type:
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


class BaseModel(ModelWorker, metaclass=BaseModelMeta):
    """A class for inheritance, passes the creation to its metaclass."""
    __abstract__ = True

    def __init__(self, *args, **kwargs):
        for (name, field_class) in self.__table__.columns.items():
            if isinstance(field_class, FieldExecutableInterface):
                if name in kwargs.keys():
                    kwargs[name] = field_class.execute(kwargs[name])
                elif not field_class.need_argument:
                    kwargs[name] = field_class.execute()

        super().__init__(*args, **kwargs)
