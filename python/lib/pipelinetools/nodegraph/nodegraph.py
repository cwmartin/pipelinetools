import networkx as nx
import weakref

from nodelib import NodeLibrary

class CycleError(Exception):pass
        
class NodeGraphExecutor(object):
    """ 
    """
    
    def execute(self, nodegraph):
        output_node = nodegraph.output_node
        cycles = nx.simple_cycles(nodegraph.graph)
        if cycles:
            raise CycleError("Cycle exists between node '%s' "\
                             "and node '%s'." % (cycles[0][0], cycles[0][1]))
                    
        self._traverse(output_node)
    
    def _traverse(self, node):            
        while True:
            #get an incoming node
            next_node = node._evaluate()
            #if no incoming nodes
            if next_node is None:                
                break            
            #traverse to that node            
            self._traverse(next_node)        
        node._graph_execute()

class NodeGraph(object):
    """
    """
    def __init__(self, parent_node=None):
        """
        """
        self._graph = nx.MultiDiGraph()
        self._parent_node = parent_node
        self._output_node = None
                        
    def _init(self):
        """
        """        
        self.add_node("input", "GraphInputNode")
        self.add_node("output", "GraphOutputNode")
        
    @property
    def graph(self):
        """        
        """
        return self._graph
    
    @property
    def output_node(self):
        """
        """
        return self._output_node
    
    @output_node.setter
    def output_node(self, output_node):
        """
        """
        self._output_node = output_node
    
    @property
    def nodes(self):
        """
        Return all nodes in this graph
        """
        return nx.topological_sort(self._graph)        
    
    def node(self, name):
        """
        """
        nodes = self._graph.nodes()
        for node in nodes:
            if node.name == name:
                return node
        return None
            
    def _get_unique_node_name(self, name):
        """
        Get a unique node name based on a given name
        @param name The base name to use.
        """
        existing_node_names = [ n.name for n in self.nodes ]
        _name = name
        inc = 1
        while _name in existing_node_names:
            _name = "%s_%i" % (name, inc)
            inc += 1        
        return _name
    
    def add_node(self, name, ntype):
        """
        Add a new node to this graph.
        @param name Name to give node.
        @param ntype The Node type class of the node to create.
        """        
        ntype = NodeLibrary.get_node_type(ntype)
        node_name = self._get_unique_node_name(name)
        node = ntype(node_name, parent=self)                        
        self._graph.add_node(node)
        return node
    
    def remove_node(self, node):
        """
        """
        
        for src_param, dst_param in node.input_connections():
            self.disconnect(src_param, dst_param)
        for src_param, dst_param in node.output_connections():
            self.disconnect(src_param, dst_param)
        
        node._parent = None
        self._graph.remove_node(node)
        
    def _add_node(self, node):
        """
        """        
        node._parent = self
        self._graph.add_node(node)
        
    def move_node(self, node, parent):
        """        
        """
        self.remove_node(node)
        parent._add_node(node)
            
    def rename_node(self, node, name):
        """
        Rename a node.
        @param node The node to rename.
        @param name Then new name to give the node.
        """
        new_name = self._get_unique_node_name(name)
        node._name = new_name
        
    def connect(self, src_param, dst_param):
        """
        Connect two node params.
        @param src_param The source param.
        @param dst_param The destination param.
        """        
        key = "%i->%i" % (id(src_param), id(dst_param))            
        self._graph.add_edge(src_param.node, dst_param.node, key=key,
                             src_param=src_param, dst_param=dst_param)
                    
        dst_param._value = weakref.ref(src_param)
        
    def disconnect(self, src_param, dst_param):
        """
        Disconnect two node params.
        @param src_param The source param.
        @param dst_param The destination param.
        """
        key = "%i->%i" % (id(src_param), id(dst_param))        
        self._graph.remove_edge(src_param.node, dst_param.node, key=key)        
        dst_param.to_default_value()
        
    def _execute(self):
        """
        """
        ex = NodeGraphExecutor()
        if self.nodes:
            ex.execute(self)
    
    def collapse(self, nodes=None):
        """
        """
        if nodes:
            subgraph = nx.subgraph(self.graph, nodes)
            graph = nx.MultiDiGraph(subgraph)
        else:
            subgraph = None
            graph = nx.MultiDiGraph(self.graph)
            self.graph.clear()
        
        subgraph_node = self.add_node("subgraph", "SubgraphNode")
        subgraph_node.nodegraph._graph = graph
        
        input_node = subgraph_node.nodegraph.add_node("input", "GraphInputNode")
        output_node = subgraph_node.nodegraph.add_node("output", "GraphOutputNode")
        
        subgraph_node.nodegraph.output_node = output_node
                        
        if subgraph:
            
            reconnect_input_params = []
            reconnect_output_params = []
                    
            #for each node in the subgraph
            for node in nodes:
                #get the input connections
                input_connections = node.input_connections()                
                for src_param, dst_param in input_connections:
                    #if the input connection is within the subgraph, skip it
                    if src_param.node in nodes:
                        continue
                    #else, add it to the reconnect list
                    reconnect_input_params.append((src_param, dst_param))
                    #disconnect the params
                    self.disconnect(src_param, dst_param)
                    
                #get the output connections
                output_connections = node.output_connections()                
                for src_param, dst_param in output_connections:
                    #if the output connection is within the subgraph, skip it
                    if dst_param in nodes:
                        continue
                    #else, add it to the reconnect list
                    reconnect_output_params.append((src_param, dst_param))
                    #disconnect the params
                    self.disconnect(src_param, dst_param)                                    
                
                #move the node to the subgraph
                node._parent = subgraph_node.nodegraph                
                self.graph.remove_node(node)
                                              
            for src_param, dst_param in reconnect_input_params:
                
                input_param = subgraph_node.add_input_param(dst_param.name, dst_param.type,
                                     default_value=dst_param.default_value)
                
                input_param.value = src_param                
                                
                input_node_param = input_node.add_output_param(input_param.name, 
                                        input_param.type, default_value=input_param.default_value)
                                                            
                #input_node_param.value = input_param                
                dst_param.value = input_node_param
                
            for src_param, dst_param in reconnect_output_params:
                
                output_param = subgraph_node.add_output_param(src_param.name, src_param.type,
                                    default_value=src_param.default_value)
                dst_param.value = output_param
                
                output_node_param = output_node.add_input_param(output_param.name,
                        output_param.type, default_value=output_param.default_value)
                
                #output_param.value = output_node_param
                output_node_param.value = src_param
        
        return subgraph_node
        
        