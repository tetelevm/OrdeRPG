"""
Configures the project settings logic, such as the installation order
and the need for settings.

You should not write any settings here unless they directly affect the
logic of the other settings.
"""


from server.utils.lib.classes.env_parser import env_parser as envs
from server.utils.settings import *

from .init_scripts import *
from .default import *


__all__ = [
    'Settings',
    'settings',
]


settings.test = envs.get_arg_from_configs_file('test')
settings.debug = envs.get_arg_from_configs_file('debug')
settings.production = envs.get_arg_from_configs_file('production')
