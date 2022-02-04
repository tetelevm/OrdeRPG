from sqlalchemy.orm import sessionmaker

from ...lib import Singleton
from .engine import DbEngine


__all_for_module__ = [
    "DbSession",
    "db_session",
]
__all__ = __all_for_module__ + [
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
