from pathlib import Path

from server.utils.settings import settings as s

# Directory with `main.py`
s.home_path = Path().resolve()
s.server_path = (Path() / 'server').resolve()
