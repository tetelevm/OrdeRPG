"""
Settings that should always be set, regardless of the others.
"""

from pathlib import Path
from server.utils.settings import settings as s

__all__ = []


# Directory with `main.py`
s.home_path = Path().resolve()
s.server_path = (Path() / 'server').resolve()
