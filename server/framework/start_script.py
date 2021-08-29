from .db.models import ModelWorker
from .db.connection import DbEngine


ModelWorker.metadata.create_all(DbEngine)
