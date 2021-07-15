import re


__all__ = [
    'camel_to_snake',
]


pattern_before = re.compile('(.)([A-Z][a-z]+)')
pattern_after = re.compile('([a-z0-9])([A-Z])')


def camel_to_snake(name):
    name = pattern_before.sub(r'\1_\2', name)
    name = pattern_after.sub(r'\1_\2', name)
    return name.lower()
