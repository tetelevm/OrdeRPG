from .db.models import ModelWorker
from .db.connection import Engine


ModelWorker.metadata.create_all(Engine)
