"""
Models to be stored in the database.
"""

from .fight import __all__ as __fight_all__
from .item import __all__ as __item_all__
from .location import __all__ as __location_all__
from .user import __all__ as __user_all__

from .fight import *
from .item import *
from .location import *
from .user import *


__all__ = (
    __user_all__
    + __fight_all__
    + __item_all__
    + __location_all__
)