from node import Node
from paramtype import VariantType  
from paramtype import StringType

class OperatorNode(Node):
    """    
    """
    def __init__(self, name, parent):
        """
        """
        super(OperatorNode, self).__init__(name, parent)
        
    def _execute(self):
        """
        """
        pass
        
class NullOperator(OperatorNode):
    """        
    """
    pass

class EchoOperator(OperatorNode):
    """
    """
    
    def _init_params(self):
        """
        """        
        self.add_input_param("echo", VariantType, default_value="")
        
    def _execute(self):
        """
        """
        print self.input_param("echo").value
        
class CodeOperator(OperatorNode):
    """        
    """
    def _init_params(self):
        """
        """        
        self.add_input_param("code", StringType)
        self.add_output_param("return", VariantType)
        
    def _compile_code(self):
        """
        """
        code_str = self.input_param("code").value
        code = compile(code_str, "<string>", "exec")
        return code
            
    def _eval(self):
        """
        """
                
        inputs = self._input_params.copy()        
        inputs.pop("code")
        inputs.pop("netin")
        
        outputs = self._output_params.copy()
        outputs.pop("netout")
                
        code = self._compile_code()    
        exec(code, {"inputs":inputs, "outputs":outputs})    
     
    def _execute(self):
        """
        """
        self._eval()
        
    
    
    
    
        
    
        
        
        
    
    
    
        