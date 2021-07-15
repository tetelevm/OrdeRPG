import os
import ast
from typing import Union

from .exceptions import ExceptionFromFormattedDoc


__all__ = [
    'EnvParser',
]


class EnvParser:
    class IncorrectStringError(ExceptionFromFormattedDoc):
        """ File "{}" str {}: string <{}> is incorrect """

    class IncorrectArgumentValueError(ExceptionFromFormattedDoc):
        """ The "{}" env argument cannot have the value <{}> """

    def __init__(self):
        self._files_cache = dict()

    def _get_arg_from_dict(self, name, args_dict, default=object):
        correct_name = ''
        value = default

        if isinstance(name, str):
            name = [name]

        for maybe_name in name:
            if not isinstance(maybe_name, str):
                raise ValueError(
                    f'{maybe_name} argument must be a <str>, not a {type(maybe_name)}')

            value = args_dict.get(maybe_name, object)
            if value is not object:
                correct_name = maybe_name
                break

        if value is object:
            if len(name) == 1:
                raise NameError(f'"{name[0]}" argument not found')
            else:
                raise NameError(f'"{name}" arguments not found')

        try:
            return ast.literal_eval(value)
        except ValueError:
            raise self.IncorrectArgumentValueError(correct_name, value)

    def _read_val_from_string(self, string0, num, file):
        string = string0.lstrip().rstrip()
        if not string:
            return ()

        string = string.split('=')
        if len(string) < 2:
            raise self.IncorrectStringError(file, num+1, string0)

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
        return self.get_arg_from_file(name, '.configs', default)
