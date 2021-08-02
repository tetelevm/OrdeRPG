"""
A class for parsing environment variables from `os.environ` or from files.
"""

import os
import ast
from typing import Union, Iterable, Mapping

from ..exceptions import ExceptionFromFormattedDoc
from .singleton import Singleton

_all_ = ['env_parser']

__all__ = _all_ + ['EnvParser']


STR_OR_ITER = Union[str, Iterable[str]]


class EnvParser(Singleton):
    # Incorrect string in the variable file
    class IncorrectStringError(ExceptionFromFormattedDoc):
        """ File "{}" str {}: string <{}> is incorrect """

    # If the argument from the environment variables is incorrect
    # For example: `object`, `list()`, `[a % 2 for a in [1, 2, 3, 4]]`
    class IncorrectArgumentValueError(ExceptionFromFormattedDoc):
        """ The "{}" env argument cannot have the value <{}> """

    def __init__(self):
        self._files_cache = dict()

    @classmethod
    def _get_arg_from_dict(cls, names: STR_OR_ITER, args_dict: Mapping, default=object):
        correct_name = ''
        value = default

        if isinstance(names, str):
            names = [names]

        for maybe_name in names:
            if not isinstance(maybe_name, str):
                raise ValueError(
                    f'{maybe_name} argument must be a <str>, not a {type(maybe_name)}')

        for maybe_name in names:
            value = args_dict.get(maybe_name, object)
            if value is not object:
                correct_name = maybe_name
                break

        if value is object:
            if len(names) == 1:
                raise NameError(f'"{names[0]}" argument not found')
            else:
                raise NameError(f'"{names}" arguments not found')

        try:
            return ast.literal_eval(value)
        except ValueError:
            raise cls.IncorrectArgumentValueError(correct_name, value)

    @classmethod
    def _read_val_from_string(cls, raw_string: str, num: int, file):
        string = raw_string.lstrip().rstrip()
        if not string or string.startswith('#'):
            return ()

        string = string.split('=')
        if len(string) < 2:
            raise cls.IncorrectStringError(file, num+1, raw_string)

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

    def get_arg_from_environ(self, name: STR_OR_ITER, default: any) -> any:
        return self._get_arg_from_dict(name, os.environ, default)

    def get_arg_from_envs_file(self, name: STR_OR_ITER, default: any) -> any:
        return self.get_arg_from_file(name, '.envs', default)

    def get_arg_from_configs_file(self, name: STR_OR_ITER, default: any) -> any:
        return self.get_arg_from_file(name, '.configs', default)


env_parser = EnvParser()
