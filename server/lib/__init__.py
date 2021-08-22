"""
A module with basic structures that use only pure Python or a standard
library.
"""

from .classes import __all__ as __classes_all__
from .func import _all_ as __func_all__
from .exceptions import __all__ as __exceptions_all__

from .classes import *
from .func import *
from .exceptions import *


__all__ = (
    __classes_all__ +
    __func_all__ +
    __exceptions_all__
)