import inspect
from nodeparam import NodeParam
    
class NodeParamType(object):
    """
    """
        
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
    
class VariantType(NodeParamType):
    """
    """
    pass

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
    
__node_types = dict([ (name, obj) for name, obj in locals().items()
           if not (name.startswith("_") or inspect.ismodule(obj)) ])

def get_param_type(name):
    """    
    """
    if name in __node_types:
        return __node_types[name]
    return None
            
