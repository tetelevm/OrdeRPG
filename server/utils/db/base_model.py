from sqlalchemy.ext.declarative import declarative_base

from server.utils.lib.func import camel_to_snake
from .fields import IdField


_all_ = [
    'BaseModel',
]

__all__ = [
    'DefaultInfo',
    'DefaultBaseModelFunctionality',
    'BaseModelMeta',
] + _all_


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
    def get_default_funks() -> dict:
        dbmf_dict = dict(DefaultBaseModelFunctionality.__dict__)
        dbmf_dict.pop('__dict__')
        dbmf_dict.pop('__weakref__')
        return dbmf_dict

    @classmethod
    def generate_dict(cls, dct: dict, clsname: str) -> dict:
        dbmf_dict = BaseModelMeta.get_default_funks()
        info = dct.get('Info', DefaultInfo)

        dct['__tablename__'] = cls._generate_tablename(info, clsname)
        dbmf_dict = cls._drop_default_pk(info, dbmf_dict)

        dct = dbmf_dict | dct
        return dct

    @staticmethod
    def _generate_tablename(info: type, clsname: str) -> str:
        tablename = getattr(info, 'tablename', None)
        if tablename is None:
            tablename = clsname.removesuffix('Model')
            tablename = camel_to_snake(tablename)
        return tablename

    @staticmethod
    def _drop_default_pk(info: type, dbmf_dict: dict) -> dict:
        if getattr(info, 'custom_pk', False):
            dbmf_dict.pop('id', None)
        return dbmf_dict


class BaseModel(metaclass=BaseModelMeta):
    pass
