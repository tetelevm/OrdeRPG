from sqlalchemy.orm import sessionmaker

from server.lib import Singleton
from .engine import DbEngine


_all_ = [
    "DbSession",
    "db_session",
]
__all__ = _all_ + [
    "DbSessionCreator",
]


DbSessionCreator = sessionmaker(bind=DbEngine)


class DbSession(Singleton):
    def __init__(self):
        self.session = DbSessionCreator()

    def add(self, *models):
        self.session.add_all(models)

    def commit(self):
        self.session.commit()


db_session = DbSession()
