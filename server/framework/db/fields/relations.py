from abc import ABC, abstractmethod
from typing import Tuple

from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm import relationship

from .base import FieldDefault


__all__ = [
    'FieldRelationshipColumn',
    'FieldRelationshipRelationship',
    'FieldRelationshipClass',
    'ForeignKeyColumn',
    'ForeignKeyRelationship',
    'ForeignKeyField',
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
    model_to = None
    parent_name: str = None
    children_name: str = None

    @abstractmethod
    def generate_id_column(self) -> Tuple[str, FieldRelationshipColumn]:
        pass

    @abstractmethod
    def generate_rel_for_c(
            self,
            c_tablename: str,
    ) -> Tuple[str, FieldRelationshipRelationship]:
        pass

    @abstractmethod
    def generate_rel_for_p(
            self,
            c_tablename: str,
            c_classname: str,
    ) -> Tuple[str, FieldRelationshipRelationship]:
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
        super().__init__(**kwargs)


class ForeignKeyRelationship(FieldRelationshipRelationship):
    def __init__(self, clsname: str, backref: str):
        super().__init__(clsname, back_populates=backref)


class ForeignKeyField(FieldRelationshipClass):
    def __init__(
            self,
            model,
            backref: str = None,
            parent_backref: str = None,
    ):
        self.model_to = model
        self.parent_name = parent_backref
        self.children_name = backref

    def generate_id_column(self) -> Tuple[str, ForeignKeyColumn]:
        parent_tablename = self.model_to.__tablename__
        column_field: FieldDefault = self.model_to.__table__.primary_key.columns[0]

        fk_name = f'{parent_tablename}.{column_field.name}'
        fk_field_name = f'{parent_tablename}_{column_field.name}'

        return (
            fk_field_name,
            ForeignKeyColumn(column_field.column_type, fk_name)
        )

    def generate_rel_for_c(
            self,
            c_tablename: str,
    ) -> Tuple[str, ForeignKeyRelationship]:
        parent_tablename = self.model_to.__tablename__

        parent_name = self.model_to.__name__
        backref = self.children_name or c_tablename

        return (
            parent_tablename,
            ForeignKeyRelationship(parent_name, backref)
        )

    def generate_rel_for_p(
            self,
            c_tablename: str,
            c_classname: str,
    ) -> Tuple[str, ForeignKeyRelationship]:
        parent_tablename = self.model_to.__tablename__
        parent_backref = self.parent_name or parent_tablename

        return (
                c_tablename,
                ForeignKeyRelationship(c_classname, parent_backref)
            )
