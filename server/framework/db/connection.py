from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..settings import settings


__all__ = ['Engine', 'SessionCreator']


Engine = create_engine(settings.database['name'], echo=False)

SessionCreator = sessionmaker()
