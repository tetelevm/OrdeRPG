from sqlalchemy.engine import create_engine
from ...settings import settings


__all_for_module__ = [
    "DbEngine",
]
__all__ = __all_for_module__


DbEngine = create_engine(settings.database["name"], echo=False)
