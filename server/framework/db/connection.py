from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..settings import settings


__all__ = ['DbEngine', 'DbSession']


DbEngine = create_engine(settings.database['name'], echo=False)

DbSession = sessionmaker(bind=DbEngine)
