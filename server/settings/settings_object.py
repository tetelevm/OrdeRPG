from server.utils.lib import Singleton
from server.utils.exceptions import ExceptionFromFormattedDoc


__all__ = [
    'Settings',
    'NoSettingError',
    'settings',
]


class NoSettingError(ExceptionFromFormattedDoc):
    """ Setting <{}> is not available in the project settings """


class Settings(metaclass=Singleton):
    def __init__(self):
        super(Settings, self).__init__()
        super(Settings, self).__setattr__('__settings', dict())

    def __getattribute__(self, attr):
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

        raise NoSettingError(attr)

    def __setattr__(self, attr, value):
        attr = str(attr).lower()
        self.__settings[attr] = value

    def __iter__(self):
        for (attr, value) in self.__settings.items():
            yield attr, value

    def __contains__(self, attr):
        return attr in self.__settings


settings = Settings()
