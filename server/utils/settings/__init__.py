"""
The submodule creates and initializes settings object.
"""

from .settings import Settings
from ..lib.classes.hasher import Hasher

# A instance of the object and its minimal configuration
settings = Settings()
settings.password_hasher = Hasher.hash
