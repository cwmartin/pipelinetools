"""
"""

class Registry(object):
    """
    """

    _registry = {}

    def __init__(self):
        """
        """
        raise NotImplementedError("Registry class '%s' should not be instantiated" % \
            self.__class__.__name__)

    @classmethod
    def get(cls, registry_key):
        """
        """
        return cls._registry.get(registry_key, None)

    @classmethod
    def register(cls, registry_key, cls_to_register):
        """
        """
        cls._registry[registry_key] = cls_to_register

    @classmethod
    def registry_keys(cls):
        """
        """
        return cls._registry.keys()


class NodeRegistry(Registry):
    """
    """
    pass

class NodeParamTypeRegistry(Registry):
    """
    """
    pass

class NodeGraphIOVersionRegistry(Registry):
    """
    """
    @classmethod
    def current_version(cls):
        return cls.get("1.0")
