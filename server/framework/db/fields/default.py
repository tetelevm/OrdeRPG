from abc import ABC, ABCMeta, abstractmethod

from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.visitors import TraversibleType
from sqlalchemy.sql.type_api import TypeEngine


__all__ = [
    'FieldDefaultMeta',
    'FieldDefault',
    'FieldExecutableInterface',
]


class FieldExecutableInterface(ABC):
    """Interface for field class with execute."""

    need_argument = True

    @abstractmethod
    def execute(self, *args, **kwargs):
        """A method called on init model."""
        pass


class FieldDefaultMeta(ABCMeta, TraversibleType):
    """
    Metaclass for `FieldDefault`.

    Made to provide extra functionality to field classes, currently
    constructing a default argument dictionary.
    """

    def __new__(mcs, clsname, bases, dct):
        dct = mcs.inherit_kwargs(bases, dct)
        return super(FieldDefaultMeta, mcs).__new__(mcs, clsname, bases, dct)

    @staticmethod
    def inherit_kwargs(bases, dct):
        """
        Constructs a default argument dictionary. Arguments of child
        classes will overwrite the same arguments of parent classes.
        """

        cls_default_kwargs = dct.get('_default_kwargs', dict())
        parent_default_kwargs = {
            key: val
            for cls in bases
            for (key, val) in getattr(cls, '_default_kwargs', dict()).items()
        }
        dct['_default_kwargs'] = parent_default_kwargs | cls_default_kwargs

        return dct


class FieldDefault(Column, metaclass=FieldDefaultMeta):
    """
    Abstract field class from which all new types of fields are
    inherited.

    If you want to create a new field class, you must inherit
    it from this class for other parts of the system to work correctly.
    """

    column_type = TypeEngine
    _default_kwargs = dict()

    def __init__(self, **kwargs):
        kwargs = self._default_kwargs | kwargs
        kwargs['type_'] = self.column_type
        super().__init__(**kwargs)

    def __repr__(self):
        return super().__repr__().replace('Column', self.__class__.__name__)

    # TODO: here and in all child classes: explore and add `params` and `unique_params`
    def params(self, *optionaldict, **kwargs):
        return super().params(*optionaldict, **kwargs)

    def unique_params(self, *optionaldict, **kwargs):
        return super().unique_params(*optionaldict, **kwargs)
