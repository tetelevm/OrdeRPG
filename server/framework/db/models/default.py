
from pydantic import create_model as create_pydantic_model

from ..fields import IdField


__all__ = [
    'DefaultInfo',
    'DefaultBaseModelFunctionality',
]


class DefaultInfo:
    """
    A class that contains meta-information about model.

    The name could (and would be more logical) be `Meta` instead of
    `Info`, but in this case it could be confused with the name of some
    metaclass.
    """

    tablename = None
    custom_pk = False


class DefaultBaseModelFunctionality:
    """
    A class with standard model settings.

    It could have been passed to `declarative_base`, but it was done that
    way for more convenience in generating other models.
    """

    __pydantic__ = create_pydantic_model('__default_model')

    id = IdField(name='id')

    class Info(DefaultInfo):
        """Instance of standard Info."""
        pass
