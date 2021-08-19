"""
Settings that should always be set, regardless of the others.
"""

from pathlib import Path
from server.framework.settings import settings as s

__all__ = []


# Directory with `main.py`
s.home_path = Path(__file__).parent.parent.parent
s.server_path = (Path() / 'server').resolve()
