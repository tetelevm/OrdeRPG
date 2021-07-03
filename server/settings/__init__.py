"""
All system settings.

The settings are logically divided into files, if you want to add your
own settings, select the necessary file.
"""


from server.utils.lib import EnvParser
from .settings_object import *
from .default import *


__all__ = [
    'Settings',
    'NoSettingError',
    'settings',
]


envs = EnvParser()
settings.test = envs.get_arg_from_env_file('test')
settings.debug = envs.get_arg_from_env_file('debug')
settings.production = envs.get_arg_from_env_file('production')
