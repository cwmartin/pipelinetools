from registry import NodeRegistry
from registry import NodeParamTypeRegistry
from nodegraph import NodeGraph
from nodeparam import NodeParam
from nodeparam import NULL_VALUE
from pipelinetools.utils.ordereddict import OrderedDict


class _NodeMeta(type):
    """
    """
    def __init__(cls, name, bases, clsdict):
        """
        """
        super(_NodeMeta, cls).__init__(name, bases, clsdict)
        NodeRegistry.register(cls.__name__, cls)

class NodeModifier(object):
    """
    """
    def _get_unique_node_name(self, node, name, mode):
        """
        Return a param name which is unique for the node based upon the given name. 
        If param_name already exists on the node for the given mode, an number is appended 
        to the name to make it unique.
        @param node Node to get a unique param name for.
        @param name Param name to test uniqueness of.
        @param mode Param mode i.e. INPUT or OUTPUT
        @returns str
        """
        _name = name
        inc = 1
        
        if mode == constants.INPUT:
            existing_params = node._input_params.keys()
        else:
            existing_params = node._output_params.keys()

        while _name in existing_params:
            _name = "%s%i" % (name, inc)
            inc += 1
        return _name

    def add_param(self, node, name, param_type, param_mode, default_value=constants.NULL_VALUE):
        """
        """
        param_name = _get_unique_param_name(node, name, param_mode)
        param = NodeParam(node, param_name, param_type, param_mode,
                      default_value=default_value, user_param=node._params_created)
        self._input_params[param_name] = param
        return param

    def remove_param(self, node, param):
        """
        """

        

    def rename_param(self, node, param, name):
        """
        """    

class Node(object):
    """
    """

    __metaclass__ = _NodeMeta

    def __init__(self, name, parent_graph, has_default_params=True):
        """
        """
        self._parent_graph = parent_graph
        self._nodegraph = NodeGraph(self)
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
            self.add_input_param("netin", NodeParamTypeRegistry.get("VariantType"))
            self.add_output_param("netout", NodeParamTypeRegistry.get("VariantType"))
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
        return self._parent_graph

    @property
    def parent_graph(self):
        """
        Return the parent NodeGraph
        @returns NodeGraph
        """
        return self._parent_graph

    @property
    def parent_node(self):
        """
        """
        return self.parent_graph._parent_node

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
        return self.parent_graph.rename(self, name)

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

    def find_param(self, name):
        """
        @param name
        @returns Tuple of (param, mode)
        """
        print "Looking for", name, "on", self
        if name in self._input_params:
            print "Found Input"
            return self._input_params[name], NodeParam.INPUT
        if name in self._output_params:
            print "Found Output"
            return self._output_params[name], NodeParam.OUTPUT

        return None

    def input_connections(self):
        """
        """
        return self.parent_graph.connections.find(dst_node=self)

    def output_connections(self):
        """
        """
        return self.parent_graph.connections.find(src_node=self)

    def connections(self, src=False, dst=True):
        """
        Get the connections to this node.
        @param src If True return the connections that this node is a source to.
        @param dst If True return the connections that this node is a destination to.        
        @returns list
        """
        conns = []
        if dst:
            input_conns = self.input_connections()
            conns.extend(input_conns)
        if src:
            output_conns = self.output_connections()
            conns.extend(output_conns)

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

    def _evaluate(self, executor):
        """
        """
        #get all input connections
        input_connections = self.parent_graph.list_connections(dst_node=self)
        #get all input nodes
        input_nodes = [ conn.src_node for conn in input_connections ]
        #filter any nodes which have already been executed
        nodes = filter(lambda x : not in executor.executed, input_nodes)
        #filter duplicates
        nodes = list(set(nodes))

        if nodes:
            #get the first node in the list
            next_node = nodes[0]
            #if the next node is a child node or next node is that parent node, skip
            #if next_node in self.nodegraph.nodes or next_node == self.parent_node:
            #    return None
            return next_node
        return None

    def _execute(self, executor):
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

        self.graph_input_node = self.nodegraph.add_node("input", "GraphInputNode")
        self.graph_output_node = self.nodegraph.add_node("output", "GraphOutputNode")


    # def add_input_param(self, name, ptype, default_value=NULL_VALUE):
    #     """
    #     Add an input param to this node.
    #     @param name The name of the param.
    #     @param ptype The NodeParamType to add.
    #     @param default The default value to give the param.
    #     @returns NodeParam
    #     """
    #     super(SubgraphNode, self).add_input_param(name, ptype, default_value=default_value)
    #     self.graph_input_node.add_output_param(name, ptype)

    # def add_output_param(self, name, ptype, default_value=NULL_VALUE):
    #     """
    #     Add an output param to this node.
    #     @param name The name of the param.
    #     @param ptype The NodeParamType to add.
    #     @param default The default value to give the param.
    #     @returns NodeParm
    #     """
    #     param_name = self._get_unique_param_name(name, NodeParam.OUTPUT)
    #     p = NodeParam(self, param_name, ptype, NodeParam.OUTPUT,
    #                   default_value=default_value, user_param=self._params_created)
    #     self._output_params[param_name] = p
    #     return p

    def child_node(self, name):
        """
        """
        return self.nodegraph.node(name)

    def _evaluate(self, executor):
        """
        """
        next_node = super(SubgraphNode, self)._evaluate(executor)
        if next_node in self.nodegraph.nodes:
            return None
        return next_node

    def _execute(self, executor):
        """
        """
        executor.execute(self.nodegraph)

class GraphInputNode(Node):
    """
    """
    def __init__(self, name, parent, nodegraph=None):
        super(GraphInputNode, self).__init__(name, parent, nodegraph=nodegraph,
                                has_default_params=False)

    def _execute(self, executor):
        """
        """
        parent_subgraph = self.parent_graph._parent_node

        for name, param in self._output_params.items():
            parent_param = parent_subgraph.input_param(name)
            parent_value = parent_param.value
            param.value = parent_value

        super(GraphInputNode, self)._execute(executor)

class GraphOutputNode(Node):
    """
    """
    def __init__(self, name, parent, nodegraph=None):
        super(GraphOutputNode, self).__init__(name, parent, nodegraph=nodegraph,
                                has_default_params=False)

    def _execute(self, executor):
        """
        """
        parent_subgraph = self.parent_graph._parent_node

        for name, param in self._input_params.items():
            parent_param = parent_subgraph.output_param(name)
            value = param.value
            parent_param.value = value

        super(GraphOutputNode, self)._execute(executor)

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
        self.add_input_param("switch_index", NodeParamTypeRegistry.get("IntegerType"),
                                default_value=0)
        self.add_input_param("index_0", NodeParamTypeRegistry.get("VariantType"))
        self.add_output_param("chosen_value", NodeParamTypeRegistry.get("VariantType"))

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

    def _evaluate(self, executor):
        """
        """
        #if switcher index has a referenced value
        if self.input_param("switch_index").is_connected:
            #if the referenced node has been executed
            ref_node =self.input_param("switch_index").connected_param_value.node
            if ref_node not in exector.executed:
                return ref_node

        indexed_param = self.get_indexed_param()
        if indexed_param.is_connected:
            indexed_node = indexed_param.connected_param_value.node
            if indexed_node not in exector.executed:
                return indexed_node
        return None

    def _execute(self, exector):
        """
        """
        self.nodegraph._execute()
        self.output_param("chosen_value").value = self.get_indexed_param().value