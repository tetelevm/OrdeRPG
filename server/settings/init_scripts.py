"""
If you need to execute any scripts when initializing a project, you are
welcome to do so here.
"""

from server.utils.lib import Hasher, env_parser

__all__ = []


Hasher.set_algorithms(env_parser.get_arg_from_configs_file('hash_algorithms', None))
