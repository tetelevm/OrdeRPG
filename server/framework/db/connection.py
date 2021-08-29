from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..settings import settings


__all__ = ['Engine', 'Session']


Engine = create_engine(settings.database['name'], echo=False)

Session = sessionmaker(bind=Engine)
