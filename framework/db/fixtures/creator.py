import graphlib

from ...lib import frozendict
from ..connection import db_session
from ..models.base import ModelWorker, BaseModelMeta
from .reader import DATA_TYPE


__all_for_module__ = ["FixtureCreator"]
__all__ = __all_for_module__


class FixtureCreator:
    data: DATA_TYPE
    models: dict[str, BaseModelMeta]

    def __init__(self, data: DATA_TYPE):
        models = [
            model.class_
            for model in ModelWorker.registry.mappers
        ]
        self.models = frozendict({
            model.__tablename__: model
            for model in models
        })
        self.data = data

    def get_creation_order(self):
        sorter = graphlib.TopologicalSorter()
        for (model_name, model_data) in self.data.items():
            sorter.add(model_name, *model_data["depends"])

        try:
            topological_order = list(sorter.static_order())
        except graphlib.CycleError as exc:
            msg = (
                "The order of the dependencies of the fixtures is looped:\n"
                + ' <-> '.join(exc.args[1])
            )
            raise ValueError(msg)

        return topological_order

    def create(self):
        order = self.get_creation_order()

        for model_name in order:
            if model_name not in self.models:
                raise ValueError(f"Model named <{model_name}> is missing")

        for model_name in order:
            model = self.models[model_name]
            data_list = self.data[model_name]["data"]
            model_list = [model(**data) for data in data_list]
            db_session.add(*model_list)
        db_session.commit()
