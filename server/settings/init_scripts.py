from server.utils.lib import EnvParser, Hasher

__all__ = []


Hasher.set_algorithms(EnvParser().get_arg_from_config_file('hash_algorithms', None))
