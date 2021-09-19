from __future__ import annotations
from abc import ABC, abstractmethod

from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import RelationshipProperty

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


# ======== INTERFACES ========


class FieldRelationshipColumn(FieldDefault, ABC):
    pass


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
    column_class = FieldRelationshipColumn
    relation_class = FieldRelationshipRelationship

    model_to = None
    parent_name: str = None
    children_name: str = None

    @abstractmethod
    def generate_id_column(
            self
    ) -> tuple[str, FieldRelationshipClass.column_class]:
        pass

    @abstractmethod
    def generate_rel_for_c(
            self,
            c_tablename: str,
    ) -> tuple[str, FieldRelationshipClass.relation_class]:
        pass

    @abstractmethod
    def generate_rel_for_p(
            self,
            c_tablename: str,
            c_classname: str,
    ) -> tuple[str, FieldRelationshipClass.relation_class]:
        pass

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


# ======== FOREIGN KEY ========


class ForeignKeyColumn(FieldRelationshipColumn):
    def __init__(self, column_type, fk_name, **kwargs):
        self.column_type = column_type
        self.parent_column = ForeignKey(fk_name)
        kwargs.setdefault('nullable', False)
        super().__init__(**kwargs)


class ForeignKeyRelationship(FieldRelationshipRelationship):
    def __init__(self, clsname: str, as_name: str, **kwargs):
        kwargs.pop('backref', None)
        kwargs.pop('back_populates', None)
        super().__init__(clsname, back_populates=as_name, **kwargs)


class ForeignKeyField(FieldRelationshipClass):
    column_class = ForeignKeyColumn
    relation_class = ForeignKeyRelationship

    def __init__(
            self,
            model,
            *,
            backref: str = None,
            parent_backref: str = None,
            column_kwargs: dict = dict(),
            self_kwargs: dict = dict(),
            parent_kwargs: dict = dict(),
    ):
        self.model_to = model
        self.parent_name = parent_backref
        self.children_name = backref
        self.column_kwargs = column_kwargs
        self.self_kwargs = self_kwargs
        self.parent_kwargs = parent_kwargs

    def generate_id_column(self) -> tuple[str, ForeignKeyColumn]:
        parent_tablename = self.model_to.__tablename__
        column_field: FieldDefault = self.model_to.__table__.primary_key.columns[0]

        fk_name = f'{parent_tablename}.{column_field.name}'
        fk_field_name = f'{parent_tablename}_{column_field.name}'
        column = self.column_class(
            column_field.column_type,
            fk_name,
            **self.column_kwargs
        )
        return fk_field_name, column

    def generate_rel_for_c(
            self,
            c_tablename: str,
    ) -> tuple[str, ForeignKeyRelationship]:
        parent_tablename = self.model_to.__tablename__

        parent_name = self.model_to.__name__
        self_from_parent_name = self.children_name or c_tablename
        for_self_rel = self.relation_class(
            parent_name,
            self_from_parent_name,
            **self.self_kwargs
        )

        return parent_tablename, for_self_rel

    def generate_rel_for_p(
            self,
            c_tablename: str,
            c_classname: str,
    ) -> tuple[str, ForeignKeyRelationship]:
        parent_tablename = self.model_to.__tablename__
        self_as_name = self.parent_name or parent_tablename
        for_parent_rel = self.relation_class(
            c_classname,
            self_as_name,
            **self.parent_kwargs
        )

        return c_tablename, for_parent_rel


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

    def generate_id_column(self) -> tuple[str, OnoToOneColumn]:
        return super().generate_id_column()

    def generate_rel_for_c(
            self,
            c_tablename: str,
    ) -> tuple[str, OnoToOneRelationship]:
        return super().generate_rel_for_c(c_tablename)

    def generate_rel_for_p(
            self,
            c_tablename: str,
            c_classname: str,
    ) -> tuple[str, OnoToOneRelationship]:
        return super().generate_rel_for_p(c_tablename, c_classname)


# ======== MANY TO MANY KEY ========


