"""
A module that is responsible for programming processes, not business
processes.

It is a kind of separate mini-framework, which is an add-on to the more
basic libraries and facilitates the construction of the main application.

Only the standard library and pip-installed modules can be imported into
this module. The module must be completely self-contained and must not
have any backward linkage to any of the files outside of `framework`.

In the files of this module you can see the `_all_` variables (in
addition to `__all__`). This is done to keep the namespace cleaner in the
higher `__init__.py`. While the `__all__` variables carry all the names
that are available (for general) import from a given file, the `_all_`
variable contains the names that will be available for import at the
level above.

Example:

smth ->
    __init__.py ->
        from file import _all_ as _file_all_
        from file import *
        __all__ = _file_all_  # ['CommonClass', ]

    file.py ->
        _all_ = ['CommonClass', ]
        __all__ = _all_ + ['SpecificClass', ]  # ['CommonClass', 'SpecificClass', ]
        class CommonClass:
            pass
        class SpecificClass:
            pass

You can import the `CommonClass`
    either `from smth.file import CommonClass`
    or     `from smth import CommonClass`

But you can only import the `SpecificClass` as
    `from smth.file import SpecificClass`
"""

from .db import __all__ as __db_all__
from .settings import __all__ as __settings_all__

from .db import *
from .settings import *


__all__ = __db_all__ + __settings_all__
