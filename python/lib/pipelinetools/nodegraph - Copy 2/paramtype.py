import inspect
from nodeparam import NodeParam
from registry import NodeParamTypeRegistry

class _NodeParamTypeMeta(type):
    """
    """
    def __init__(cls, name, bases, clsdict):
        """
        """
        super(_NodeParamTypeMeta, cls).__init__(name, bases, clsdict)        
        NodeParamTypeRegistry.register(cls.__name__, cls)

class NodeParamType(object):
    """
    """
    __metaclass__ = _NodeParamTypeMeta

    @classmethod
    def compatible(cls, value):
        """
        """
        if isinstance(value, NodeParam):
            val = value.value
        else:
            val = value
        try:
            cls.convert(val)
            return True
        except:
            return False
        
    @classmethod
    def default_value(cls):
        """
        """
        return None
        
    @classmethod
    def convert(cls, value):
        """
        """
        return value   
    
#@register_param_type()
class VariantType(NodeParamType):
    """
    """
    pass

#@register_param_type()
class StringType(NodeParamType):
    """
    """
            
    @classmethod
    def convert(cls, value):
        """
        """
        if value is None:
            return ""
        return str(value)

    @classmethod
    def default_value(cls):
        """
        """
        return ""

#@register_param_type()   
class NumericType(NodeParamType):
    """
    """    
    
    @classmethod
    def convert(cls, value):
        """
        """
        try:
            return int(value)
        except ValueError:
            return float(value)
        
    @classmethod
    def default_value(cls):
        """
        """
        return 0
        
class IntegerType(NumericType):
    """
    """
    pass

class FloatType(NumericType):
    """
    """
    pass

class ListType(NodeParamType):
    """
    """    
    @classmethod
    def default_value(cls):
        """
        """
        return []
    
class DictType(NodeParamType):
    """    
    """
    @classmethod
    def default_value(cls):
        """
        """
        return {}

def get_param_type(name):
    """    
    """
    return NodeParamTypeRegistry.get(name)    



            
