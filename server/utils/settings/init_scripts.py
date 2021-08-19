"""
Executes the initial initialization of the project settings.
"""

from server.lib.classes.hasher import Hasher
from server.lib.classes.env_parser import env_parser

from .settings import Settings


settings = Settings()
settings.password_hasher = Hasher.hash

env_parser.settings = settings
