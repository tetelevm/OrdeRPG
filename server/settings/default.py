from pathlib import Path

from server.utils.settings import settings as s
from server.utils.lib import EnvParser, Hasher

__all__ = []


# Directory with `main.py`
s.home_path = Path().resolve()
s.server_path = (Path() / 'server').resolve()


Hasher.set_algorithms(EnvParser().get_arg_from_config_file('hash_algorithms', None))
s.password_hasher = Hasher.hash
