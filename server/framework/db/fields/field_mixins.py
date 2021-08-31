from abc import ABC, abstractmethod


__all__ = [
    'FieldExecutable',
    'FieldMixinMinMax',
]


class FieldExecutable(ABC):
    """Interface for field class with execute."""

    need_argument = True

    @abstractmethod
    def execute(self, *args, **kwargs):
        """A method called on init model."""
        pass


class FieldMixinMinMax(FieldExecutable):
    min_value: float = None
    max_value: float = None

    def execute(self, *args, **kwargs):
        value = kwargs.get('value', 0)
        if getattr(self, 'min_value', None) is not None:
            value = max(value, self.min_value)
        if getattr(self, 'max_value', None) is not None:
            value = min(value, self.max_value)
        return value
