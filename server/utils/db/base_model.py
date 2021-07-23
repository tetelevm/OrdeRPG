from sqlalchemy.ext.declarative import declarative_base

from server.utils.lib import camel_to_snake
from .fields import IdField


__all__ = [
    'DefaultInfo',
    'DefaultBaseModelFunctionality',
    'BaseModelMeta',
    'BaseModel',
]


ModelGenerator = declarative_base(name='ModelGenerator')


class DefaultInfo:
    tablename = None
    custom_pk = False


class DefaultBaseModelFunctionality(object):
    id = IdField()

    class Info(DefaultInfo):
        pass


class BaseModelMeta(type):
    def __new__(mcs, clsname, bases, dct):
        if clsname == 'BaseModel':
            return type.__new__(mcs, clsname, bases, dct)

        bases = tuple(set(bases) - {BaseModel})
        dct = mcs.generate_dict(dct, clsname)

        cls = type(clsname, bases, {})
        return type(clsname, (cls, ModelGenerator), dct)

    @staticmethod
    def generate_dict(dct: dict, clsname: str) -> dict:
        dbmf_dict = BaseModelMeta.get_default_funks()

        info = dct.get('Info', DefaultInfo)

        # Set tablename
        tablename = getattr(info, 'tablename', None)
        if tablename is None:
            tablename = clsname.removesuffix('Model')
            tablename = camel_to_snake(tablename)
        dct['__tablename__'] = tablename

        # Drop default pk
        if getattr(info, 'custom_pk', False):
            dbmf_dict.pop('id', None)

        dct = dbmf_dict | dct
        return dct

    @staticmethod
    def get_default_funks() -> dict:
        dbmf_dict = dict(DefaultBaseModelFunctionality.__dict__)
        dbmf_dict.pop('__dict__')
        dbmf_dict.pop('__weakref__')
        return dbmf_dict


class BaseModel(metaclass=BaseModelMeta):
    pass
