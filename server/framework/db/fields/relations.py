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


REL_TYPE = 'Relationship'


class FieldRelationshipColumn(FieldDefault, ABC):
    pass


class FieldRelationshipRelationship(RelationshipProperty, ABC):
    RELATIONSHIP_TYPE: str = REL_TYPE

    def __str__(self):
        return '{r_type} to <{model_to}> (as {backref})'.format(
            r_type=self.RELATIONSHIP_TYPE,
            model_to=self.argument,
            backref=self.backref,
        )

    def __repr__(self):
        return '{r_type}(to={model_to}, as={backref})'.format(
            r_type=self.RELATIONSHIP_TYPE,
            model_to=self.argument,
            backref=self.backref,
        )


GENERATED = Tuple[
    Tuple[str, FieldRelationshipColumn],
    Tuple[str, FieldRelationshipRelationship],
    Tuple[str, FieldRelationshipRelationship],
]


class FieldRelationshipClass(ABC):
    RELATIONSHIP_TYPE: str = REL_TYPE
    model_to = None
    parent_name: str = None
    children_name: str = None

    @abstractmethod
    def generate_fields(self, self_classname: str, self_tablename: str) -> GENERATED:
        pass

    def __str__(self):
        to_name = (
            self.model_to.__name__
            if self.model_to is not None else
            '(unknown)'
        )
        return '{r_type} to {model_to}'.format(
            r_type=self.RELATIONSHIP_TYPE,
            model_to=to_name,
        )

    def __repr__(self):
        to_name = (
            self.model_to.__name__
            if self.model_to is not None else
            '(unknown)'
        )
        return '{r_type}(to={model_to})'.format(
            r_type=self.RELATIONSHIP_TYPE,
            model_to=to_name,
        )


# ======== FOREIGN KEY ========


FK_TYPE = 'ForeignKey'


class ForeignKeyFieldColumn(FieldRelationshipColumn):
    def __init__(self, column_type, fk_name, **kwargs):
        self.column_type = column_type
        self.parent_column = ForeignKey(fk_name)
        super().__init__(**kwargs)


class ForeignKeyFieldRelationship(FieldRelationshipRelationship):
    RELATIONSHIP_TYPE = FK_TYPE

    def __init__(self, clsname: str, backref: str):
        super().__init__(clsname, backref=backref)


GENERATED_FK = Tuple[
    Tuple[str, ForeignKeyFieldColumn],
    Tuple[str, ForeignKeyFieldRelationship],
    Tuple[str, ForeignKeyFieldRelationship],
]


class ForeignKeyField(FieldRelationshipClass):
    RELATIONSHIP_TYPE = FK_TYPE

    def __init__(
            self,
            model,
            backref: str = None,
            parent_backref: str = None,
    ):
        self.model_to = model
        self.parent_name = parent_backref
        self.children_name = backref

    def _generate_id(self) -> Tuple[str, ForeignKeyFieldColumn]:
        parent_tablename = self.model_to.__tablename__
        column_field: FieldDefault = self.model_to.__table__.primary_key.columns[0]

        fk_name = f'{parent_tablename}.{column_field.name}'
        fk_field_name = f'{parent_tablename}_{column_field.name}'

        return (
            fk_field_name,
            ForeignKeyFieldColumn(column_field.column_type, fk_name)
        )

    def _generate_rel_for_c(
            self,
            c_tablename: str
    ) -> Tuple[str, ForeignKeyFieldRelationship]:
        parent_tablename = self.model_to.__tablename__

        parent_name = self.model_to.__name__
        backref = self.children_name or c_tablename

        return (
            parent_tablename,
            ForeignKeyFieldRelationship(parent_name, backref)
        )

    def _generate_rel_for_p(
            self,
            c_classname: str,
            c_tablename: str
    ) -> Tuple[str, ForeignKeyFieldRelationship]:
        parent_tablename = self.model_to.__tablename__
        parent_backref = self.parent_name or parent_tablename

        return (
                c_tablename,
                ForeignKeyFieldRelationship(c_classname, parent_backref)
            )

    def generate_fields(self, c_classname: str, c_tablename: str) -> GENERATED_FK:
        column_id_info = self._generate_id()
        relationship_for_c_info = self._generate_rel_for_c(c_tablename)
        relationship_for_p_info = self._generate_rel_for_p(c_classname, c_tablename)
        return (
            column_id_info,
            relationship_for_c_info,
            relationship_for_p_info,
        )
