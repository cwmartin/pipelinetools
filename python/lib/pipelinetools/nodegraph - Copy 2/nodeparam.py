import weakref

NULL_VALUE = "__NULL__VALUE__"

class NodeParam(object):
    
    INPUT = 0
    OUTPUT = 1
    
    def __init__(self, node, name, type, mode, default_value=NULL_VALUE,
                 user_param=False):
        """
        """
        self._node = node
        self._name = name
        self._type = type
        self._value = NULL_VALUE
        self._mode = mode
        self._default_value = default_value
        self._user_param = user_param
                
    @property
    def node(self):
        """
        Return node param.
        """        
        return self._node
    
    @property
    def name(self):        
        """
        Return param name
        """
        return self._name
    
    @property
    def mode(self):
        """
        Return param mode
        """
        return self._mode
    
    @property
    def is_user_param(self):
        """
        Return True is param is a user added param.
        """
        return self._user_param
    
    def rename(self, name):
        """
        Rename parame.
        @param name New param name.
        """
        return self.node.rename_param(self, name)
                
    @property
    def type(self):
        """
        Return the type of this param        
        """
        return self._type
    
    @property
    def default_value(self):
        """
        @Return the default value for this param.
        """
        if self._default_value != NULL_VALUE:
            return self._default_value            
        return self._type.default_value()
    
    @property    
    def has_default_value(self):
        """
        Return True if this param has an overridden default value.
        """
        return self._default_value != NULL_VALUE
        
    def to_default_value(self):
        """
        Restore the value of this param to it's default value.
        """
        self._value = NULL_VALUE
        
    def compatible(self, param):
        """
        Test if a NodeParam is compatible with this NodeParam.
        @param param NodeParam to test compatibility.
        """
        return self._type.compatible(param.value)

    @property
    def is_connected(self):
        """
        """
        return isinstance(self._value, weakref.ReferenceType)

    @property
    def connected_param_value(self):
        """
        """
        if self.is_connected:
            return self._value()
        return None

    @property
    def is_passthru(self):
        """
        """        
        if self.is_connected:
            connected_param = self.connected_param_value            
            connections = self.node.parent.connections.find(src_param=connected_param,
                                            dst_param=self, ignore_passthru=False)            
            if connections:                
                return connections[0].is_passthru
        return False
            
    @property
    def value(self):
        """
        Get the value of the param        
        """        
        if self._value == NULL_VALUE:
            return self.default_value
        
        if isinstance(self._value, weakref.ReferenceType):                        
            value = self._value()                        
            if value is None:
                return None            
        else:
            value = self._value  

        if isinstance(value, NodeParam):
            return_value = value.value            
            return self._type.convert(return_value)            
    
        return value
    
    @value.setter
    def value(self, value):
        """
        Set the value of the param.
        """                    
        if isinstance(self._value, weakref.ReferenceType):
            curr_value = self._value()            
        else:
            curr_value = self._value
            
        if isinstance(curr_value, NodeParam):                    
            self._node.parent.disconnect(curr_value, self)

        self._value = value
                    
        # if isinstance(value, NodeParam):
        #     self._node.parent.connect(value, self)
        # else:
        #     self._value = value

            
    def __repr__(self):
        return "%s.%s" % (self.node, self._name)