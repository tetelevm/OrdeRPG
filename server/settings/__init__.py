"""
Configures the project settings logic, such as the installation order
and the need for settings.

You should not write any settings here unless they directly affect the
logic of the other settings.
"""

from framework.lib.classes import env_parser as envs
from framework.settings import settings


__all__ = ["settings"]


def import_default():
    from .default import __all__


def set_run_context():
    settings.test = envs.get_arg_from_configs_file("test")
    settings.debug = envs.get_arg_from_configs_file("debug")
    settings.production = envs.get_arg_from_configs_file("production")


def run_init_scripts():
    from .init_scripts import __all__


import_default()
set_run_context()
run_init_scripts()
