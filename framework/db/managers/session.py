from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from ...lib import Singleton
from ...settings import settings


__all_for_module__ = [
    "DbEngine",
    "DbSession",
    "db_session",
]
__all__ = __all_for_module__ + [
    "DbSessionCreator",
]


DbEngine = create_engine(settings.database["name"], echo=False)

DbSessionCreator = sessionmaker(bind=DbEngine)


class DbSession(Singleton):
    def __init__(self):
        self.session = DbSessionCreator()

    def add(self, *models):
        self.session.add_all(models)

    def commit(self):
        self.session.commit()


db_session = DbSession()
