from .db.models import ModelWorker
from .db.managers import DbEngine


ModelWorker.metadata.create_all(DbEngine)
