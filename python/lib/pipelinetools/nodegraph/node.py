from nodegraph import NodeGraph
from nodeparam import NodeParam
from nodeparam import NULL_VALUE
from paramtype import VariantType
from paramtype import IntegerType
from pipelinetools.utils.ordereddict import OrderedDict
    
class Node(object):
    """
    """    
    def __init__(self, name, parent, nodegraph=None, has_default_params=True):
        """
        """            
        self._parent = parent        
        self._nodegraph = nodegraph or NodeGraph(self)
        self._name = name
        self._has_default_params = has_default_params
        
        self._input_params = OrderedDict()
        self._output_params = OrderedDict()
        
        self._params_created = False                
        self.__init_params()
        self._params_created = True
        
        self._executed = False
            
    def __init_params(self):
        """
        Initialize node parameters.
        """                
        if self._has_default_params:
            self.add_input_param("netin", VariantType)
            self.add_output_param("netout", VariantType)           
        self._init_params()
    
    def _init_params(self):
        """
        """
        pass
            
    @property
    def parent(self):
        """
        Return the parent NodeGraph
        @returns NodeGraph
        """
        return self._parent
    
    @property
    def nodegraph(self):
        """
        Return the node's NodeGraph
        @returns NodeGraph
        """
        return self._nodegraph
        
    @property
    def name(self):
        """
        Return the node's name
        @returns str
        """
        return self._name
    
    def rename(self, name):
        """
        Rename the node.
        @param name The new node name.
        @returns str
        """
        return self.parent.rename(self, name)
    
    def input_param(self, name):
        """
        Get an input param by name.
        @param name. The name of the param to get.
        @returns NodeParam
        """
        return self._input_params.get(name, None)
    
    def output_param(self, name):
        """
        Get an output param by name.
        @param name. The name of the param to get
        @returns NodeParam
        """
        return self._output_params.get(name, None)
    
    def input_connections(self):
        """
        """
        edges = self.parent.graph.in_edges(self, data=True)
        input_connections = [ (edge[2]["src_param"], edge[2]["dst_param"]) for edge in edges]
        return input_connections
    
    def output_connections(self):
        """
        """                
        
        edges = self.parent.graph.out_edges(self, data=True)            
        output_connections = [ (edge[2]["src_param"], edge[2]["dst_param"]) for edge in edges]        
        return output_connections
        
    def connections(self, src=False, dst=True, params=True):
        """
        Get the connections to this node.
        @param src If True return the connections that this node is a source to.
        @param dst If True return the connections that this node is a destination to.
        @param params If True return node parameters, else return just nodes.
        @returns list        
        """        
        conns = []
        if params:
            if src:
                #grab the node params that this node is a src to
                edges = self.parent.graph.out_edges(self, data=True)            
                conns.extend([ edge[2]["dst_param"] for edge in edges ])
            if dst:
                #grab the node param that this node is a dst to
                edges = self.parent.graph.in_edges(self, data=True)                
                conns.extend([ edge[2]["src_param"] for edge in edges ])
        else:                
            if src:
                conns.extend(self.parent.graph.successors(self))
            if dst:
                conns.extend(self.parent.graph.predecessors(self))
            
        return conns
    
    def _get_unique_param_name(self, name, mode):
        """
        Get a unique param name.
        @param name The base name.
        @param mode. The NodeParam mode.
        @returns str
        """
        _name = name
        inc = 1
        
        if mode == NodeParam.INPUT:
            existing_params = self._input_params
        else:
            existing_params = self._output_params
            
        while _name in existing_params:
            _name = "%s%i" % (name, inc)        
            inc += 1            
        return _name
    
    def rename_param(self, param, name):
        """
        Rename a param.
        @param param Then param to rename.
        @param name The new param name.
        @returns str
        """
        old_name = param.name
        new_name = self._get_unique_param_name(name, param.mode)
        
        param._name = new_name
        
        if param.mode == NodeParam.INPUT:
            self._input_params.pop(old_name)
            self._input_params[new_name] = param
        else:
            self._output_params.pop(old_name)
            self._output_params[new_name] = param
        
        return new_name
    
    def add_input_param(self, name, ptype, default_value=NULL_VALUE):
        """
        Add an input param to this node.
        @param name The name of the param.
        @param ptype The NodeParamType to add.
        @param default The default value to give the param.
        @returns NodeParam
        """        
        param_name = self._get_unique_param_name(name, NodeParam.INPUT)        
        p = NodeParam(self, param_name, ptype, NodeParam.INPUT, 
                      default_value=default_value, user_param=self._params_created)            
        self._input_params[param_name] = p
        return p
                    
    def add_output_param(self, name, ptype, default_value=NULL_VALUE):
        """
        Add an output param to this node.
        @param name The name of the param.
        @param ptype The NodeParamType to add.
        @param default The default value to give the param.
        @returns NodeParm
        """        
        param_name = self._get_unique_param_name(name, NodeParam.OUTPUT)
        p = NodeParam(self, param_name, ptype, NodeParam.OUTPUT, 
                      default_value=default_value, user_param=self._params_created)            
        self._output_params[param_name] = p
        return p
    
    def _evaluate(self):
        """
        """
        #print "Evaluating", self
        nodes = filter(lambda x : not x._executed, self.connections(params=False))        
        if nodes:
            return nodes[0]
        return None
    
    def _graph_execute(self):
        """        
        """
        #print "Executing", self        
        self._execute()
        self._executed = True
        
    def _execute(self):
        """        
        """
        pass
            
    def __str__(self):
        return self._name
    
    def __repr__(self):
        return self.__str__()
    
class SubgraphNode(Node):
    """
    """
    def __init__(self, name, parent, nodegraph=None):
        super(SubgraphNode, self).__init__(name, parent, nodegraph=nodegraph,
                                has_default_params=False)
        
    def _execute(self):
        """
        """
        self.nodegraph._execute()
        

class GraphInputNode(Node):
    """
    """
    def __init__(self, name, parent, nodegraph=None):
        super(GraphInputNode, self).__init__(name, parent, nodegraph=nodegraph,
                                has_default_params=False)
        
    def _execute(self):
        """
        """
        parent_subgraph = self.parent._parent_node
        
        for name, param in self._output_params.items():
            parent_param = parent_subgraph.input_param(name)            
            parent_value = parent_param.value
            param.value = parent_value
            
        super(GraphInputNode, self)._execute()
            

class GraphOutputNode(Node):
    """
    """
    def __init__(self, name, parent, nodegraph=None):
        super(GraphOutputNode, self).__init__(name, parent, nodegraph=nodegraph,
                                has_default_params=False)
        
    def _execute(self):
        """
        """
        parent_subgraph = self.parent._parent_node
        
        for name, param in self._input_params.items():
            parent_param = parent_subgraph.output_param(name)
            value = param.value
            parent_param.value = value
            
        super(GraphOutputNode, self)._execute()
    
class SwitchNode(Node):
    """    
    """
    def __init__(self, name, parent, nodegraph=None):
        """
        """
        super(SwitchNode, self).__init__(name, parent, nodegraph=nodegraph,
                                         has_default_params=False)
    
    def _init_params(self):
        """
        """
        self.add_input_param("switch_index", IntegerType, default_value=0)
        self.add_input_param("index_0", VariantType)
        self.add_output_param("chosen_value", VariantType)
        
    def get_indexed_param(self):
        """
        Get the parameter indexed by the switch index.
        @returns NodeParam
        """
        switcher_index = self.input_param("switch_index").value                
        indexed_param = self.input_param("index_%s" % switcher_index)
        if indexed_param is None:
            raise Exception("Switch index value for %s is out of bouned." % self)
        return indexed_param
        
    def _evaluate(self):
        """
        """
        print "Evaluating", self
        #if switcher index has a referenced value
        if self.input_param("switch_index").has_referenced_value():
            #if the referenced node has been executed
            ref_node =self.input_param("switch_index").referenced_value().node
            if not ref_node._executed:
                return ref_node
        
        indexed_param = self.get_indexed_param()
        if indexed_param.has_referenced_value():
            indexed_node = indexed_param.referenced_value().node
            if not indexed_node._executed:
                return indexed_node 
        return None
    
    def _execute(self):
        """        
        """
        self.nodegraph._execute()
        self.output_param("chosen_value").value = self.get_indexed_param().value
        