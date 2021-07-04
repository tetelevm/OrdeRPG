__all__ = [
    'ExceptionFromDoc',
    'ExceptionFromFormattedDoc',
]


class ExceptionFromDoc(Exception):
    """ Something went wrong """
    def __init__(self, msg=None):
        if msg is None:
            msg = self.__doc__
        super(ExceptionFromDoc, self).__init__(msg.lstrip().rstrip())


class ExceptionFromFormattedDoc(ExceptionFromDoc):
    __doc__ = ExceptionFromDoc.__doc__

    def __init__(self, *formats):
        try:
            msg = self.__doc__.format(*formats)
        except IndexError:
            msg = 'The error could not be formatted, but an error of the form\n'
            msg += self.__doc__ + '\n'
            msg += str(formats)
        super(ExceptionFromFormattedDoc, self).__init__(msg)
