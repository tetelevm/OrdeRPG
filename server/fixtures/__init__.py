from pathlib import Path
from framework.db.fixtures import FixtureReader, FixtureCreator
from server.models import *


__all__ = ["create_fixtures"]


FIXTURE_FOLDER_PATH = Path(__file__).absolute().parent.absolute()


def create_fixtures():
    reader = FixtureReader(FIXTURE_FOLDER_PATH)
    creator = FixtureCreator(reader.data)
    creator.create()
