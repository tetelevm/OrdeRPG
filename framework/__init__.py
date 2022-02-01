"""
A module that is responsible for programming processes, not business
processes.

It is a kind of separate mini-framework, which is an add-on to the more
basic libraries and facilitates the construction of the main application.

Only the standard library and pip-installed modules can be imported into
this module. The module must be completely self-contained and must not
have any backward linkage to any of the files outside of `framework`.

------------------------------------------------------------------------

In the files of this module you can see the `__all_for_module__`
variables (in addition to `__all__`). This is done to keep the namespace
cleaner in the higher `__init__.py`. While the `__all__` variables carry
all the names that are available (for general) import from a given file,
the `__all_for_module__` variable contains the names that will be
available for import at the level above.

Example:

smth ->
    | file.py ->
    | |-------------------------------------
    | | __all_for_module__ = ['CommonClass', ]
    | | __all__ = __file_all__ + ['SpecificClass', ]  # ['CommonClass', 'SpecificClass', ]
    | | class CommonClass:
    | |     pass
    | | class SpecificClass:
    | |     pass
    | |-------------------------------------
    |
    | __init__.py ->
    | |-------------------------------------
    | | from file import __all_for_module__ as __file_all__
    | | from file import *
    | | __all__ = __file_all__  # ['CommonClass', ]
    | |-------------------------------------

You can import the `CommonClass`
    either `from smth.file import CommonClass`
    or     `from smth import CommonClass`

But you can only import the `SpecificClass` as
    `from smth.file import SpecificClass`
"""

from .db import __all_for_module__ as __db_all__
from .lib import __all_for_module__ as __lib_all__
from .settings import __all_for_module__ as __settings_all__

from .db import *
from .lib import *
from .settings import *


__all__ = __db_all__ + __lib_all__ + __settings_all__
