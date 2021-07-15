from sqlalchemy.ext.declarative import declarative_base

from server.utils.lib import camel_to_snake


__all__ = [
    'BaseModel',
]


class DefaultBaseFunctionality:
    def __new__(cls):
        tablename = cls.__name__.removesuffix('Model')
        tablename = camel_to_snake(tablename)
        cls.__tablename__ = tablename
        return super().__new__(cls)


BaseModel = declarative_base(cls=DefaultBaseFunctionality)
BaseModel.__tablename__ = ''
