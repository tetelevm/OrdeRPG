"""
A module with basic structures that use only pure Python or a standard
library.
"""

from .classes import __all_for_module__ as __classes_all__
from .func import __all_for_module__ as __func_all__
from .exceptions import __all_for_module__ as __exceptions_all__

from .classes import *
from .func import *
from .exceptions import *


__all_for_module__ = (
    __classes_all__ +
    __func_all__ +
    __exceptions_all__
)
__all__ = __all_for_module__
