"""
Does not import or use any functions or constants from other parts of
the system. Only the standard library is imported here.
"""

import os
import ast
from typing import Union


class EnvParser:
    def __init__(self):
        self._files_cache = dict()

    @staticmethod
    def _get_arg_from_dict(name, args_dict, default):
        correct_name = ''
        value = default

        if isinstance(name, str):
            name = [name]

        for name_ in name:
            if not isinstance(name_, str):
                raise ValueError(
                    f'{name_} argument must be a <str>, not a {type(name_)}')

            value = args_dict.get(name_, object)
            if value is not object:
                correct_name = name_
                break

        if value is object:
            raise KeyError(f'No env argument "{correct_name}"')

        try:
            return ast.literal_eval(value)
        except ValueError:
            raise ValueError(
                f'The "{correct_name}" env argument cannot have the value "{value}"')

    @staticmethod
    def _read_val_from_string(string0, num, file):
        string = string0.lstrip().rstrip()
        if not string:
            return ()

        string = string.split('=')
        if len(string) < 2:
            raise ValueError(
                f'file <{file}>:<{num}> - string <<{string0}>> is incorrect'
            )

        if len(string) > 2:
            string = [string[0], '='.join(string[1:])]

        string = (string[0].rstrip(), string[1].lstrip())
        return string

    def _read_file_into_cache(self, file_path) -> None:
        with open(file_path) as file:
            data = file.read()

        data = filter(
            None,
            (self._read_val_from_string(string, i, file_path)
                for (i, string) in enumerate(data.split('\n')))
        )
        data = {key: val for (key, val) in data}
        self._files_cache[file_path] = data

    def get_arg_from_file(self, name, file_path, default):
        if file_path not in self._files_cache:
            self._read_file_into_cache(file_path)
        return self._get_arg_from_dict(name, self._files_cache[file_path], default)

    def get_arg_from_env(self, name: Union[str, iter], default: any = object) -> any:
        return self._get_arg_from_dict(name, os.environ, default)

    def get_arg_from_env_file(self, name: Union[str, iter], default: any = object) -> any:
        return self.get_arg_from_file(name, '.envs', default)

    def get_arg_from_config_file(self, name: Union[str, iter], default: any = object) -> any:
        return self.get_arg_from_file(name, '.config', default)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
