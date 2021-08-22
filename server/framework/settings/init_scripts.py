"""
Executes the initial initialization of the project settings.
"""

from server.lib.classes.hasher import Hasher
from server.lib.classes.env_parser import env_parser

from .settings import Settings


settings = Settings()
settings.password_hasher = Hasher.hash

settings.database = {
    'name': 'sqlite://'
}

# Backref and another config

env_parser.settings = settings
