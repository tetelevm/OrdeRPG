from sqlalchemy.ext.declarative import declarative_base

from server.utils.lib import camel_to_snake
from .fields import IdField

__all__ = [
    'DefaultMeta',
    'DefaultBaseModelFunctionality',
    'BaseModel',
]


ModelGenerator = declarative_base(name='ModelGenerator')


class DefaultMeta:
    tablename = None
    custom_pk = False


class DefaultBaseModelFunctionality:
    id = IdField()
    ZZZ = 123123

    class Meta(DefaultMeta):
        pass


class ModelGeneratorMeta(type):
    def __new__(mcs, clsname, bases, dct):
        if clsname == 'BaseModel':
            return type.__new__(mcs, clsname, bases, dct)

        bases = tuple(set(bases) - {BaseModel})
        dct = mcs.generate_dict(dct)
        cls = type(clsname, bases, dct)

        cls = mcs.construct_class(cls)
        return type(clsname, (cls, ModelGenerator), {})

    @staticmethod
    def generate_dict(dct):
        dbmf_dict = dict(DefaultBaseModelFunctionality.__dict__)
        dbmf_dict.pop('__dict__')
        dbmf_dict.pop('__weakref__')
        dct = dbmf_dict | dct
        return dct

    @staticmethod
    def construct_class(cls: type) -> type:
        meta = cls.Meta

        tablename = getattr(meta, 'tablename', None)
        if tablename is None:
            tablename = cls.__name__.removesuffix('Model')
            tablename = camel_to_snake(tablename)
        cls.__tablename__ = tablename

        if getattr(meta, 'custom_pk', False):
            del cls.id

        return cls


class BaseModel(metaclass=ModelGeneratorMeta):
    pass
