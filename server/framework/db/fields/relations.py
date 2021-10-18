from __future__ import annotations
from abc import ABC, abstractmethod

from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm.decl_api import DeclarativeMeta

from server.lib import ExceptionFromFormattedDoc
from ..models.utils import get_model_primary_key, PostInitCreator
from .base import FieldDefault


_all_ = [
    'FieldRelationshipColumn',
    'FieldRelationshipRelationship',
    'FieldRelationshipClass',

    'ForeignKeyColumn',
    'ForeignKeyRelationship',

    'OnoToOneColumn',
    'OnoToOneRelationship',
]
__all__ = _all_ + [
    'ForeignKeyField',
    'OnoToOneField',
]


class AlreadyExistsError(ExceptionFromFormattedDoc):
    """<{}> field of <{}> class is already occupied (current value is <{}>)"""


# ======== INTERFACES ========


class FieldRelationshipColumn(FieldDefault, ABC):
    def __init__(self, column_type, fk_name, **kwargs):
        self.column_type = column_type
        self.parent_column = ForeignKey(fk_name)
        kwargs.setdefault('nullable', False)

        super().__init__(**kwargs)


class FieldRelationshipRelationship(RelationshipProperty, ABC):
    def __str__(self):
        return '{r_type} to <{model_to}> (as {backref})'.format(
            r_type=self.__class__.__name__,
            model_to=self.argument,
            backref=self.backref,
        )

    def __repr__(self):
        return '{r_type}(to={model_to}, as={backref})'.format(
            r_type=self.__class__.__name__,
            model_to=self.argument,
            backref=self.backref,
        )


class FieldRelationshipClass(ABC):
    model_to = None
    parent_name: str = None
    children_name: str = None

    def __str__(self):
        to_name = (
            self.model_to.__name__
            if self.model_to is not None else
            '(unknown)'
        )
        return '{r_type} to {model_to}'.format(
            r_type=self.__class__.__name__,
            model_to=to_name,
        )

    def __repr__(self):
        to_name = (
            self.model_to.__name__
            if self.model_to is not None else
            '(unknown)'
        )
        return '{r_type}(to={model_to})'.format(
            r_type=self.__class__.__name__,
            model_to=to_name,
        )

    @abstractmethod
    def generate_fields(
            self,
            clsname: str,
            field_name: str,
            dct: dict,
    ) -> None:
        pass


# ======== FOREIGN KEY ========


class ForeignKeyColumn(FieldRelationshipColumn):
    pass


class ForeignKeyRelationship(FieldRelationshipRelationship):
    def __init__(self, clsname: str, as_name: str, **kwargs):
        kwargs.pop('backref', None)
        kwargs.pop('back_populates', None)
        to = kwargs.pop('to_table', clsname)
        super().__init__(to, back_populates=as_name, **kwargs)


class ForeignKeyField(FieldRelationshipClass):
    column_class = ForeignKeyColumn
    relation_class = ForeignKeyRelationship

    def __init__(
            self,
            model,
            *,
            backref: str = None,
            column_kwargs: dict = None,
            self_kwargs: dict = None,
            parent_kwargs: dict = None,
    ):
        column_kwargs = (column_kwargs is not None and column_kwargs) or dict()
        self_kwargs = (self_kwargs is not None and self_kwargs) or dict()
        parent_kwargs = (parent_kwargs is not None and parent_kwargs) or dict()

        self.model_to = model
        self.children_name = backref
        self.column_kwargs = column_kwargs
        self.self_kwargs = self_kwargs
        self.parent_kwargs = parent_kwargs

    def postinit_create_field(
            self,
            model_from: DeclarativeMeta,
            clsname: str,
            field_name: str,
    ):
        self_tablename = model_from.__tablename__
        parent_tablename = self.model_to.__tablename__
        parent_pk_field: FieldDefault = get_model_primary_key(self.model_to)
        parent_clsname = self.model_to.__name__
        parent_fieldname = self.children_name or self_tablename

        # set database column
        fk_column_code = f'{parent_tablename}.{parent_pk_field.name}'
        fk_field_name = f'{parent_tablename}_{parent_pk_field.name}'
        fk_type = parent_pk_field.column_type

        if hasattr(model_from, fk_field_name):
            attr = getattr(model_from, fk_field_name)
            raise AlreadyExistsError(fk_field_name, clsname, attr.__repr__())
        column = self.column_class(fk_type, fk_column_code, **self.column_kwargs)
        setattr(model_from, fk_field_name, column)

        # set parent relationship
        if hasattr(self.model_to, parent_fieldname):
            attr = getattr(self.model_to, parent_fieldname)
            raise AlreadyExistsError(
                parent_fieldname,
                parent_clsname,
                attr.__repr__()
            )
        parent_relation = self.relation_class(clsname, field_name, **self.parent_kwargs)
        setattr(self.model_to, parent_fieldname, parent_relation)

        # set self relationship
        self_relation = self.relation_class(parent_clsname, parent_fieldname, **self.self_kwargs)
        setattr(model_from, field_name, self_relation)

    def generate_fields(
            self,
            clsname: str,
            field_name: str,
            dct: dict,
    ) -> None:
        action = PostInitCreator(self.postinit_create_field, clsname, field_name)
        dct['_postinit_actions'].append(action)


# ======== ONE TO ONE KEY ========


class OnoToOneColumn(ForeignKeyColumn):
    pass


class OnoToOneRelationship(ForeignKeyRelationship):
    def __init__(self, clsname: str, as_name: str, **kwargs):
        kwargs['uselist'] = False
        super().__init__(clsname, as_name, **kwargs)


class OnoToOneField(ForeignKeyField):
    column_class = OnoToOneColumn
    relation_class = OnoToOneRelationship

# ======== MANY TO MANY KEY ========

