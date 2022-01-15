import graphlib

from ...lib import frozendict
from ..models.base import ModelWorker
from .reader import DATA_TYPE


__all_for_module__ = ["FixtureCreator"]
__all__ = __all_for_module__


class FixtureCreator:
    data: DATA_TYPE

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
        self.separate_m2m_fields()

    def separate_m2m_fields(self):
        pass

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

