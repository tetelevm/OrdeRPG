"""
If you need to execute any scripts when initializing a project, you are
welcome to do so here.
"""

from server.utils.lib import EnvParser, Hasher

__all__ = []


Hasher.set_algorithms(EnvParser().get_arg_from_config_file('hash_algorithms', None))
