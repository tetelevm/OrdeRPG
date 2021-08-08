"""
A class for parsing environment variables from `os.environ` or from files.
"""

import os
import ast
from typing import Union, Iterable, Mapping

from ..exceptions import ExceptionFromFormattedDoc


_all_ = ['env_parser']
__all__ = _all_ + ['EnvParser']


STR_OR_ITER = Union[str, Iterable[str]]
FROM_STRING_TYPE = tuple[Union[tuple[str, str], tuple], bool]
DEFAULT_OBJ = object()


class EnvParser:
    """
    A class that collects and defines an environment variable.

    The main method of class is `get_arg_from_dict`, which searches and
    translates into python-view the necessary values.

    It also has an important method `get_arg_from_file` in which it reads
    the specified file and searches it for desired values.
    """

    class IncorrectStringError(ExceptionFromFormattedDoc):
        """ Incorrect string in the variable file. """
        __doc__ = """ File "{}" str {}: string <{}> is incorrect """

    def __init__(self):
        self._files_cache = dict()

    @staticmethod
    def get_arg_from_dict(
            names: STR_OR_ITER,
            args_dict: Mapping[str, str],
            default: any = DEFAULT_OBJ,
            translate: bool = True,
    ) -> any:
        """
        Searches for one or more variable names in the dictionary, and
        then translates the variable value from string to Python value.

        >>> EnvParser.get_arg_from_dict('foo', {'foo': '100'})
        >>> # 100
        >>>
        >>> EnvParser.get_arg_from_dict(
        >>>    ['foo', 'bar'], {'bar': '{"a": 1, "b": 2}'})
        >>> # {'a': 1, 'b': 2}
        >>>
        >>> EnvParser.get_arg_from_dict(['foo', 'bar'], {'spam': '100'})
        >>> # NameError: "['foo', 'bar']" arguments not found
        >>>
        >>> EnvParser.get_arg_from_dict('foo', {'bar': '100'}, 300)
        >>> # 300
        >>>
        >>> EnvParser.get_arg_from_dict('foo', {'foo': 'bar'})
        >>> # ValueError: The "foo" env argument cannot have value <bar>
        >>>
        >>> EnvParser.get_arg_from_dict(
        >>>     'foo', {'foo': 'bar'}, translate=False)
        >>> # 'bar'
        >>>
        >>> EnvParser.get_arg_from_dict(
        >>>     'foo', {'bar': 'spam'}, 'eggs', translate=False)
        >>> # 'eggs'
        """

        if isinstance(names, str):
            names = [names]
        # Names must be only strings
        names = [str(name) for name in names]

        for maybe_name in names:
            if maybe_name not in args_dict:
                continue

            correct_name = maybe_name
            value = args_dict[maybe_name]

            if translate:
                try:
                    value = ast.literal_eval(value)
                except ValueError:
                    # Argument from the environment variables is incorrect
                    # Example: `object`, `list()`, `[a % 2 for a in [1, 2, 3]]`
                    error = 'The "{}" env argument cannot have value <{}>'
                    raise ValueError(error.format(correct_name, value))
            break
        else:
            value = default

        if value is not DEFAULT_OBJ:
            return value

        if len(names) == 1:
            error = f'"{names[0]}" argument not found'
        else:
            error = f'"{names}" arguments not found'
        raise NameError(error)

    def _read_file_into_cache(self, file_path) -> None:
        """
        Reads and parses config file and writes results to own cache.
        """

        def read_val_from_string(raw_string: str) -> FROM_STRING_TYPE:
            """
            Parses line by `=` sign and returns variable name with value
            and success result. If the string begins with `#` it is
            skipped.

            >>> read_val_from_string('')
            >>> # ((), True)
            >>>
            >>> read_val_from_string('# Comment')
            >>> # ((), True)
            >>>
            >>> read_val_from_string('count = 100')
            >>> # (('count', '100'), True)
            >>> read_val_from_string('  string    ="st=ri=ng"   ')
            >>> # (('string', '"st=ri=ng"'), True)
            >>>
            >>> read_val_from_string('line without equal sign')
            >>> # ((), False)
            """

            string = raw_string.lstrip().rstrip()
            if not string or string.startswith('#'):
                return (), True

            eq_index = string.find('=')
            if eq_index == -1:
                return (), False

            name, value = string[:eq_index], string[eq_index + 1:]
            name, value = name.rstrip(), value.lstrip()

            return (name, value), True

        with open(file_path) as file:
            text = file.read()

        data = dict()
        for (i, string) in enumerate(text.split('\n')):
            result, succ = read_val_from_string(string)
            if not succ:
                raise self.IncorrectStringError(file_path, i + 1, string)
            if result:
                data[result[0]] = result[1]

        self._files_cache[file_path] = data

    def get_arg_from_file(self, name: str, file_path, *args, **kwargs):
        """
        Reads the file, writes received data to cache and searches the
        file's cache for desired values.
        """

        if file_path not in self._files_cache:
            self._read_file_into_cache(file_path)

        return self.get_arg_from_dict(name, self._files_cache[file_path],
                                      *args, **kwargs)

    @classmethod
    def get_arg_from_environ(cls, name: STR_OR_ITER, *args, **kwargs) -> any:
        """
        A wrapper around `.get_arg_from_dict()` that sets up `os.environ`
        in the `args_dict: Mapping` variable in advance.
        """

        return cls.get_arg_from_dict(name, os.environ, *args, **kwargs)

    def get_arg_from_envs_file(self, name: STR_OR_ITER, *args, **kwargs) -> any:
        """
        A wrapper around `.get_arg_from_file()` that sets up '.envs' file
        in the `file_path` variable in advance.
        """

        return self.get_arg_from_file(name, '.envs', *args, **kwargs)

    def get_arg_from_configs_file(self, name: STR_OR_ITER, *args, **kwargs) -> any:
        """
        A wrapper around `.get_arg_from_file()` that sets up '.configs'
        file in the `file_path` variable in advance.
        """

        return self.get_arg_from_file(name, '.configs', *args, **kwargs)


env_parser = EnvParser()
