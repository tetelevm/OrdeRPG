from pathlib import Path
from framework.db.utils import FixtureCreator
from server.models import *


__all__ = ["create_fixtures"]


FIXTURE_FOLDER_PATH = Path(__file__).absolute().parent.absolute()


def create_fixtures():
    creator = FixtureCreator(FIXTURE_FOLDER_PATH)
    creator.create()
