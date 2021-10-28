import yaml
import json
import graphlib
from typing import Callable, IO, Optional, Any

from ...lib.func import get_all_files_from_directory_generator, frozendict


_all_ = ["FixtureReader"]
__all__ = _all_ + [
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


class FixtureReader:
    def __init__(self, data_path=None, data_type='yaml'):
        self.supported_types = frozendict({
            "yaml": self.add_data_from_yaml,
            "json": self.add_data_from_json,
        })

        self.data: DATA_TYPE = dict()
        if data_path:
            self.add_data_from_type(data_path, data_type)

    def add_data_from_type(self, data_path, data_type='yaml'):
        try:
            method = self.supported_types[data_type]
        except KeyError:
            msg = (
                "{type} type is not supported. Try to parse the data yourself"
                " and add the already processed data."
            ).format(type=repr(data_type))
            raise ValueError(msg)

        method(data_path)

    def add_data_from_yaml(self, data_path):
        filter_yaml = lambda f: (f.endswith(".yaml") or f.endswith(".yml"))
        parse_yaml = yaml.safe_load
        self.pasre_data_from_files(data_path, filter_yaml, parse_yaml)

    def add_data_from_json(self, data_path):
        filter_json = lambda f: f.endswith(".json")
        parse_json = json.load
        self.pasre_data_from_files(data_path, filter_json, parse_json)

    def add_data(self, data: DATA_TYPE):
        for (tablename, model_data) in data.items():
            model_data = self.prepare_data(tablename, model_data)
            if tablename in self.data:
                self.extend_model_data(tablename, model_data)
            else:
                self.data[tablename] = model_data

    # ==============================

    def pasre_data_from_files(
            self,
            data_path,
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

    def sort_data(self):
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
