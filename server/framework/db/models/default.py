from ..fields import IdField
from .utils import generate_pydantic_model


__all__ = [
    'DefaultInfo',
    'get_default_model_dict',
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


def get_default_model_dict() -> dict:
    """
    Translates `DefaultBaseModelFunctionality` class data into a
    dictionary and converts the dictionary to the desired form.
    """
    class DefaultBaseModelFunctionality:
        """
        A class with standard model settings.

        It could have been passed to `declarative_base`, but it was done that
        way for more convenience in generating other models.
        """

        __pydantic__ = None
        id = IdField(name='id')

    dbmf_dict = dict(DefaultBaseModelFunctionality.__dict__)
    to_pop = ['__dict__', '__doc__', '__module__', '__weakref__']
    for key in to_pop:
        dbmf_dict.pop(key)

    dbmf_dict['__pydantic__'] = generate_pydantic_model(
        dbmf_dict, model_name='__default_model')

    return dbmf_dict
