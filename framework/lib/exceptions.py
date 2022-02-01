"""
The submodule contains useful utilities for exceptions.
"""

__all_for_module__ = [
    "ExceptionFromDoc",
    "ExceptionFromFormattedDoc",
]
__all__ = __all_for_module__


class ExceptionFromDoc(Exception):
    """
    Outputs as an error value that is specified for the class in the
    docstring.

    >>> class Error(ExceptionFromDoc):
    >>>     '''String from docstring'''
    >>> raise Error()
    >>> # Error: String from docstring
    """
    __doc__ = """Something went wrong"""

    def __init__(self, msg=None):
        if msg is None:
            msg = self.__doc__
        super().__init__(msg.lstrip().rstrip())


class ExceptionFromFormattedDoc(ExceptionFromDoc):
    """
    It formats string from docstring with values given during
    initialization and then returns it at error.

    If you pass fewer arguments than you need for formatting, you will
    be notified. But be careful, because if you pass too many arguments,
    the extra ones will be hidden.

    >>> class NoFormatException(ExceptionFromFormattedDoc):
    >>>     '''Unformatted line from docstring'''
    >>> raise NoFormatException()
    >>> # NoFormatException: Unformatted line from docstring

    >>> class FormatException(ExceptionFromFormattedDoc):
    >>>     '''Foo value <{}>, bar value "{}"'''
    >>> raise FormatException('foo', ['bar'])
    >>> # FormatException: Foo value <foo>, bar value "['bar']"

    >>> raise FormatException('foo')
    >>> # FormatException: The error could not be formatted, but an error of the form
    >>> # Foo value <{}>, bar value "{}"
    >>> # ('foo',)

    >>> raise FormatException('foo', ['bar'], 'spam')
    >>> # FormatException: Foo value <foo>, bar value "['bar']"
    """
    __doc__ = ExceptionFromDoc.__doc__

    def __init__(self, *formats):
        try:
            msg = self.__doc__.format(*formats)
        except IndexError:
            msg = "The error could not be formatted, but an error of the form"
            msg += "\n"
            msg += self.__doc__
            msg += "\n"
            msg += str(formats)
        super().__init__(msg)
