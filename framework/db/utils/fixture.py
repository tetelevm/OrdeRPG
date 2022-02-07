import json
import graphlib
from pathlib import Path
from typing import Callable, IO, Optional, Any

import yaml

from ...lib.func import get_all_files_from_directory_generator, frozendict
from ..managers.session import db_session
from ..models.base import ModelWorker, BaseModelMeta


__all_for_module__ = ["FixtureCreator"]
___all__ = __all_for_module__ + [
    "TABLENAME",
    "FIELD_NAME",
    "FIELD_VALUE",
    "MODEL_DATA",
    "TABLE_DATA",
    "DATA_TYPE",
]


TABLENAME = str
FIELD_NAME = str
FIELD_VALUE = Any

MODEL_DATA = dict[FIELD_NAME, FIELD_VALUE]
TABLE_DATA = dict[
    [
        Optional["depends"],
        list[TABLENAME]
    ],
    [
        "data",
        list[MODEL_DATA]
    ],
]

DATA_TYPE = dict[TABLENAME, TABLE_DATA]


class FixtureCreator:
    data: DATA_TYPE
    models: frozendict[str, BaseModelMeta]
    supported_types: dict[str, Callable[[str | Path], None]]

    def __init__(self, data_path: str | Path = None, data_type: str = "yaml"):
        self.supported_types = {
            "json": self.add_data_from_json,
            "yaml": self.add_data_from_yaml,
        }

        self.models = frozendict({
            model.class_.__tablename__: model.class_
            for model in ModelWorker.registry.mappers
        })

        self.data = dict()
        if data_path:
            self.add_data_from_type(data_path, data_type)

    def add_data_from_yaml(self, data_path: str | Path):
        filter_yaml = lambda f: (f.endswith(".yaml") or f.endswith(".yml"))
        parse_yaml = yaml.safe_load
        self.pasre_data_from_files(data_path, filter_yaml, parse_yaml)

    def add_data_from_json(self, data_path: str | Path):
        filter_json = lambda f: f.endswith(".json")
        parse_json = json.load
        self.pasre_data_from_files(data_path, filter_json, parse_json)

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

    # ==============================

    def add_data_from_type(self, data_path: str | Path, data_type: str = "yaml"):
        try:
            method = self.supported_types[data_type]
        except KeyError:
            msg = (
                "{type} type is not supported. Try to parse the data yourself"
                " and add the already processed data."
            ).format(type=repr(data_type))
            raise ValueError(msg)

        method(data_path)

    def add_data(self, data: DATA_TYPE):
        for (tablename, model_data) in data.items():
            model_data = self.prepare_data(tablename, model_data)
            if tablename in self.data:
                self.extend_model_data(tablename, model_data)
            else:
                self.data[tablename] = model_data

    def get_creation_order(self):
        sorter = graphlib.TopologicalSorter()
        for (model_name, model_data) in self.data.items():
            sorter.add(model_name, *model_data["depends"])

        try:
            topological_order = list(sorter.static_order())
        except graphlib.CycleError as exc:
            msg = (
                    "The order of the dependencies of the fixtures is looped:\n"
                    + " <-> ".join(exc.args[1])
            )
            raise ValueError(msg)

        return topological_order

    def pasre_data_from_files(
            self,
            data_path: str | Path,
            filter_func: Callable[[str], bool],
            parse_func: Callable[[IO], DATA_TYPE],
    ):
        files = get_all_files_from_directory_generator(data_path, filter_func)
        for file in files:
            file_data = parse_func(open(file))
            self.add_data(file_data)

    def extend_model_data(self, tablename: str, model_data: TABLE_DATA):
        current_data = self.data[tablename]

        current_depends = set(current_data["depends"])
        new_depends = set(model_data["depends"])
        current_data["depends"] = list(current_depends | new_depends)

        current_data["data"].extend(model_data["data"])

    @staticmethod
    def prepare_data(tablename: str, data: TABLE_DATA) -> TABLE_DATA:
        if "data" not in data:
            raise ValueError(
                f"There is no <data> attribute in the {tablename} model")

        data.setdefault("depends", [])
        return data
