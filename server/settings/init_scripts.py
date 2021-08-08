"""
If you need to execute any scripts when initializing a project, you are
welcome to do so here.
"""

from server.utils import Hasher, env_parser


__all__ = []


algorithms = env_parser.get_arg_from_configs_file('hash_algorithms', None)
Hasher.set_algorithms(algorithms)
