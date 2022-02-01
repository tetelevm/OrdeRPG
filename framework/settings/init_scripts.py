"""
Executes the initial initialization of the project settings.
"""

from ..lib.classes.hasher import Hasher
from ..lib.classes.env_parser import env_parser

from .settings import Settings


__all__ = ["settings"]


settings = Settings()
settings.password_hasher = Hasher.hash

settings.database = {
    "type": "sqlite",
    "name": "sqlite://",
}

# Backref and another config

env_parser.settings = settings
