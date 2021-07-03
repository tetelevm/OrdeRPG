from pathlib import Path

from .settings_object import settings as s

# Directory with `main.py`
s.home_path = Path().resolve()
s.server_path = (Path() / 'server').resolve()
