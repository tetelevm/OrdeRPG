"""
A submodule with individual classes.
"""

from .env_parser import __all_for_module__ as __env_parser_all__
from .hasher import __all_for_module__ as __hasher_all__
from .singleton import __all_for_module__ as __singleton_all__

from .env_parser import *
from .hasher import *
from .singleton import *


__all_for_module__ = (
    __env_parser_all__ +
    __hasher_all__ +
    __singleton_all__
)
__all__ = __all_for_module__
