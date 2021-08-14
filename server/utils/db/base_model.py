"""
File with the model for inheritance in other database models. Also here is
the metaclass that generates the models, and the default model settings.
"""

from pydantic import create_model as create_pydantic_model
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

from server.utils.lib.func import camel_to_snake
from .fields import FieldDefault, IdField


_all_ = ['BaseModel']
__all__ = _all_ + [
    'DefaultInfo',
    'DefaultBaseModelFunctionality',
    'BaseModelMeta',
]


ModelGenerator = declarative_base(name='ModelGenerator')


class DefaultInfo:
    """
    A class that contains meta-information about model.

    The name could (and would be more logical) be `Meta` instead of
    `Info`, but in this case it could be confused with the name of some
    metaclass.
    """

    tablename = None
    custom_pk = False


class DefaultBaseModelFunctionality:
    """
    A class with standard model settings.

    It could have been passed to `declarative_base`, but it was done that
    way for more convenience in generating other models.
    """

    id = IdField()
    __pynotation__ = create_pydantic_model('__default_model')

    class Info(DefaultInfo):
        """Instance of standard Info."""
        pass


class BaseModelMeta(DeclarativeMeta):
    """
    The main metaclass for generating database models.

    - injects standard data from `DefaultBaseModelFunctionality`
    - creates a `pydantic` model
    - set `__tablename__
    """

    def __new__(mcs, clsname, bases, dct):
        dct = mcs.generate_dict(dct, clsname)
        return super(BaseModelMeta, mcs).__new__(mcs, clsname, bases, dct)

    @classmethod
    def generate_dict(cls, dct: dict, clsname: str) -> dict:
        """
        The main method of the class. Executes all necessary logic on
        the new model class.
        """

        dbmf_dict = BaseModelMeta.get_default_model_dict()
        info = dct.get('Info', DefaultInfo)

        dct['__tablename__'] = cls._generate_tablename(info, clsname)

        dbmf_dict = cls._drop_default_pk(info, dbmf_dict)
        dct = dbmf_dict | dct

        dct['__pynotation__'] = cls._generate_pydantic_model(dct)

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

        fields = dict()
        for (name, field) in dct.items():
            if not isinstance(field, FieldDefault):
                continue

            py_type = field.type.python_type
            default = None
            if field.default is None and not field.nullable:
                default = ...

            fields[name] = (py_type, default)

        return create_pydantic_model(dct['__tablename__'], **fields)


class BaseModel(ModelGenerator, metaclass=BaseModelMeta):
    """A class for inheritance, passes the creation to its metaclass."""
    __abstract__ = True
