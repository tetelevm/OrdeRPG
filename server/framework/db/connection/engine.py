from sqlalchemy import create_engine
from ...settings import settings


__all__ = ['DbEngine',]


DbEngine = create_engine(settings.database['name'], echo=False)
