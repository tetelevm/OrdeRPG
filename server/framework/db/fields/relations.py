from abc import ABC, abstractmethod
from typing import Tuple

from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import RelationshipProperty

from .base import FieldDefault


__all__ = [
    'FieldRelationshipClass',
    'FieldRelationshipColumn',
    'ForeignKeyField',
]


# ======== INTERFACES ========


class FieldRelationshipColumn(FieldDefault, ABC):
    pass


class FieldRelationshipRelationship(RelationshipProperty, ABC):
    pass


GENERATED = Tuple[
    Tuple[str, FieldRelationshipColumn],
    Tuple[str, FieldRelationshipRelationship],
    Tuple[str, FieldRelationshipRelationship],
]


class FieldRelationshipClass(ABC):
    model_to = None
    parent_name: str = None
    children_name: str = None

    @abstractmethod
    def generate_fields(self, self_classname: str, self_tablename: str) -> GENERATED:
        pass


# ======== FOREIGN KEY ========


class ForeignKeyFieldColumn(FieldRelationshipColumn):
    def __init__(self, column_type, fk_name, **kwargs):
        self.column_type = column_type
        self.parent_column = ForeignKey(fk_name)
        super().__init__(**kwargs)


class ForeignKeyFieldRelationship(FieldRelationshipRelationship):
    def __init__(self, clsname, backref):
        super().__init__(clsname, backref=backref)


GENERATED_FK = Tuple[
    Tuple[str, ForeignKeyFieldColumn],
    Tuple[str, ForeignKeyFieldRelationship],
    Tuple[str, ForeignKeyFieldRelationship],
]


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

    def generate_fields(self, c_classname: str, c_tablename: str) -> GENERATED_FK:

        parent_name = self.model_to.__name__
        parent_tablename = self.model_to.__tablename__

        column_field: FieldDefault = self.model_to.__table__.primary_key.columns[0]
        fk_name = f'{parent_tablename}.{column_field.name}'
        fk_field_name = f'{parent_tablename}_{column_field.name}'
        column = ForeignKeyFieldColumn(column_field.column_type, fk_name)

        relationship_to_p = ForeignKeyFieldRelationship(c_classname, parent_tablename)

        relationship_to_c = ForeignKeyFieldRelationship(parent_name, c_tablename)

        return (
            (fk_field_name, column),
            (parent_tablename, relationship_to_c),
            (c_tablename, relationship_to_p),
        )
