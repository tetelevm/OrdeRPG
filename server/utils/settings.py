"""
The file contains a singleton class of settings.

This class is minimally configurable here, but the main business settings
should take place in a special sub-module in the application.
"""

from .lib import Singleton, ExceptionFromFormattedDoc
from .lib.classes.hasher import Hasher


__all__ = [
    'Settings',
    'settings',
]


class Settings(Singleton):
    """
    Setting class with customized configuration access.

    Translates all attributes when set/get to `.lower()`,
    calls `NoSettingError` when missing.

    >>> settings.smth = 123
    >>> settings.smth  # 123
    >>> settings.SmTh  # 123
    >>> settings.other_smth
    >>> # settings.NoSettingError: Setting <other_smth> is not available
    >>> # in the project settings
    >>> 'smth' in settings  # True
    >>> 'SMTH' in settings  # True
    >>> 'other_smth' in settings  # False
    >>> list(settings)  # [('smth', 123), ]

    P.S. The `settings.NoSettingError` attribute cannot be assigned.
    """

    # Custom exceptions for in case a certain setting is missing
    class NoSettingError(ExceptionFromFormattedDoc):
        """ Setting <{}> is not available in the project settings """

    def __init__(self):
        super(Settings, self).__init__()
        super(Settings, self).__setattr__('__settings', dict())

    def __getattribute__(self, attr: str) -> any:
        try:
            return super(Settings, self).__getattribute__(attr)
        except AttributeError:
            pass

        settings_dict = self.__dict__['__settings']
        if attr in ['_Settings__settings', '__settings']:
            return settings_dict

        attr = str(attr).lower()
        if attr in settings_dict:
            return settings_dict[attr]

        raise self.NoSettingError(attr)

    def __setattr__(self, attr: str, value: any):
        attr = str(attr).lower()
        self.__settings[attr] = value

    def __iter__(self):
        for (attr, value) in self.__settings.items():
            yield attr, value

    def __contains__(self, attr: str) -> bool:
        attr = attr.lower()
        return attr in self.__settings


# A instance of the object and its minimal configuration
settings = Settings()
settings.password_hasher = Hasher.hash
