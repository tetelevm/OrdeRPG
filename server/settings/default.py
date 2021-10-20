"""
Settings that should always be set, regardless of the others.
"""

from pathlib import Path
from server.lib.classes import env_parser as envs
from server.framework.settings import settings as s

__all__ = []


# Directory with `main.py`
s.home_path = Path(__file__).parent.parent.parent
s.server_path = (Path() / "server").resolve()

s.hash_salt = envs.get_arg_from_envs_file("hash_salt")
