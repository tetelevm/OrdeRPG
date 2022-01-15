from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union

from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm.decl_api import DeclarativeMeta

from ...lib import ExceptionFromFormattedDoc
from ..models.utils import get_model_primary_key, PostInitCreator
from .base import FieldDefault
from .custom import IdField


__all_for_module__ = [
    "FieldRelationshipColumn",
    "FieldRelationshipRelationship",
    "FieldRelationshipClass",

    "ForeignKeyColumn",
    "ForeignKeyRelationship",

    "OnoToOneColumn",
    "OnoToOneRelationship",

    "ManyToManyColumn",
    "ManyToManyRelationship",
]
__all__ = __all_for_module__ + [
    "ForeignKeyField",
    "OnoToOneField",
    "ManyToManyField",
]


class AlreadyExistsError(ExceptionFromFormattedDoc):
    """<{}> field of <{}> class is already occupied (current value is <{}>)"""


# ======== INTERFACES ========


class FieldRelationshipColumn(FieldDefault, ABC):
    def __init__(self, column_type, fk_name, **kwargs):
        self.column_type = column_type
        self.parent_column = ForeignKey(fk_name)
        kwargs.setdefault("nullable", False)

        super().__init__(**kwargs)


class FieldRelationshipRelationship(RelationshipProperty, ABC):
    def __str__(self):
        return "{r_type} to <{model_to}> (as {backref})".format(
            r_type=self.__class__.__name__,
            model_to=self.argument,
            backref=self.backref,
        )

    def __repr__(self):
        return "{r_type}(to={model_to}, as={backref})".format(
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
            "(unknown)"
        )
        return "{r_type} to {model_to}".format(
            r_type=self.__class__.__name__,
            model_to=to_name,
        )

    def __repr__(self):
        to_name = (
            self.model_to.__name__
            if self.model_to is not None else
            "(unknown)"
        )
        return "{r_type}(to={model_to})".format(
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

    @staticmethod
    def get_model_pk_options(
            model: DeclarativeMeta
    ) -> tuple[FieldDefault, str, str]:
        parent_tablename = model.__tablename__
        parent_pk_field: FieldDefault = get_model_primary_key(model)

        fk_column_type = parent_pk_field.column_type
        fk_column_code = f"{parent_tablename}.{parent_pk_field.name}"
        fk_field_name = f"{parent_tablename}_{parent_pk_field.name}"
        return fk_column_type, fk_column_code, fk_field_name


# ======== FOREIGN KEY ========


class ForeignKeyColumn(FieldRelationshipColumn):
    pass


class ForeignKeyRelationship(FieldRelationshipRelationship):
    def __init__(self, clsname: str, as_name: str, **kwargs):
        kwargs.pop("backref", None)
        back_populates = kwargs.pop("back_populates", as_name)
        to = kwargs.pop("to_table", clsname)

        super().__init__(to, back_populates=back_populates, **kwargs)


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
        parent_clsname = self.model_to.__name__
        parent_fieldname = self.children_name or self_tablename

        # set database column
        parent_pk_options = self.get_model_pk_options(self.model_to)
        (fk_type, fk_column_code, fk_field_name) = parent_pk_options

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
        self_relation = self.relation_class(
            parent_clsname,
            parent_fieldname,
            **self.self_kwargs
        )
        setattr(model_from, field_name, self_relation)

    def generate_fields(
            self,
            clsname: str,
            field_name: str,
            dct: dict,
    ) -> None:
        action = PostInitCreator(self.postinit_create_field, clsname, field_name)
        dct["_postinit_actions"].append(action)


# ======== ONE TO ONE KEY ========


class OnoToOneColumn(ForeignKeyColumn):
    pass


class OnoToOneRelationship(ForeignKeyRelationship):
    def __init__(self, clsname: str, as_name: str, **kwargs):
        kwargs["uselist"] = False
        super().__init__(clsname, as_name, **kwargs)


class OnoToOneField(ForeignKeyField):
    column_class = OnoToOneColumn
    relation_class = OnoToOneRelationship


# ======== MANY TO MANY KEY ========


class ManyToManyColumn(FieldRelationshipColumn):
    pass


class ManyToManyRelationship(FieldRelationshipRelationship):
    def __init__(
            self,
            clsname: str = None,
            through: Union[str, DeclarativeMeta] = None,
            as_name: str = None,
            **kwargs
    ):
        if isinstance(through, DeclarativeMeta):
            clsname = through.__name__
            through = through.__tablename__

        if as_name is None:
            as_name = kwargs.pop("back_populates", None)
        if as_name is not None:
            kwargs.pop("backref", None)
            kwargs["back_populates"] = as_name

        kwargs.pop("secondary", None)

        super().__init__(
            clsname,
            secondary=through,
            **kwargs
        )


class ManyToManyField(FieldRelationshipClass):
    def __init__(
            self,
            model,
            *,
            backref: str = None,
            self_kwargs: dict = None,
            parent_kwargs: dict = None,
            through: DeclarativeMeta = None,
    ):
        self_kwargs = (self_kwargs is not None and self_kwargs) or dict()
        parent_kwargs = (parent_kwargs is not None and parent_kwargs) or dict()

        self.model_to = model
        self.children_name = backref
        self.self_kwargs = self_kwargs
        self.parent_kwargs = parent_kwargs
        self.through = through

    def postinit_create_model(self, model: DeclarativeMeta):
        parent_tname = self.model_to.__tablename__
        parent_clsname = self.model_to.__name__
        child_tname = model.__tablename__
        child_clsname = model.__name__

        tablename = f"m2m_{parent_tname}_{child_tname}"
        clsname = f"M2M_{parent_clsname}_{child_clsname}"
        if self.children_name is None:
            self.children_name = child_tname

        (
            (child_type, child_fk_code, child_fk_name),
            (parent_type, parent_fk_code, parent_fk_name),
        ) = (
            self.get_model_pk_options(model),
            self.get_model_pk_options(self.model_to),
        )

        child_fk = ManyToManyColumn(child_type, child_fk_code)
        parent_fk = ManyToManyColumn(parent_type, parent_fk_code)

        Info = type("Info", (), {"tablename": tablename, "default_pk": False})
        self.through = model.__class__(
            clsname,
            (model.__class__.base_model,),
            {
                "id": IdField(autoincrement=False),
                "Info": Info,
                child_fk_name: child_fk,
                parent_fk_name: parent_fk,
            }
        )

    def set_fields(self, model: DeclarativeMeta, field_name: str):
        child_rel = ManyToManyRelationship(
            self.model_to.__name__,
            self.through.__tablename__,
            self.children_name,
            **self.self_kwargs
        )
        parent_rel = ManyToManyRelationship(
            model.__name__,
            self.through.__tablename__,
            field_name,
            **self.parent_kwargs
        )
        setattr(model, field_name, child_rel)
        setattr(self.model_to, self.children_name, parent_rel)

    def add_model_to_m2m_models(self, model):
        model._m2m_models[self.model_to.__tablename__] = self.through
        self.model_to._m2m_models[model.__tablename__] = self.through

    def generate_fields(
            self,
            clsname: str,
            field_name: str,
            dct: dict,
    ) -> None:
        dct.pop(field_name)
        if self.through is None:
            dct["_postinit_actions"].append(self.postinit_create_model)

        set_fields = PostInitCreator(self.set_fields, field_name)
        dct["_postinit_actions"].append(set_fields)

        add_action = self.add_model_to_m2m_models
        dct["_postinit_actions"].append(add_action)
