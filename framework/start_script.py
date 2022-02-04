from .db.models import ModelWorker
from .db.peel import DbEngine


ModelWorker.metadata.create_all(DbEngine)
