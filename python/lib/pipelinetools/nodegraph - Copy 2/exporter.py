import json
from nodegraph import NodeGraph
from nodeparam import NodeParam 
from nodeparam import NULL_VALUE
from registry import NodeGraphIOVersionRegistry
import paramtype
import nodelib
import graphing
from pipelinetools.utils.ordereddict import OrderedDict
import nodegraphmodifier as ngm

class _NodeGraphIOMeta(type):
    """
    """
    def __init__(cls, name, bases, clsdict):
        """
        """
        super(_NodeGraphIOMeta, cls).__init__(name, bases, clsdict)        
        NodeGraphIOVersionRegistry.register(cls.VERSION, cls)

class NodeGraphIO(object):
    """
    """

    __metaclass__ = _NodeGraphIOMeta

    VERSION = "1.0"

    def _export_param(self, param, export_connections=True):
        """
        """     
        is_passthru = False

        if param.is_connected:                  
            if export_connections:  
                value = param.connected_param_value
                is_passthru = param.is_passthru
                value = str(value)
                reference = True
            else:
                value = param.default_value
                reference = False
        else:
            value = param.value
            reference = False
        
        export = OrderedDict()
        export["name"] = param.name
        export["type"] = param.type.__name__                
        export["value"] = value
        export["reference"] = reference
        #export["passthru"] = is_passthru
                    
        if param.has_default_value:
            export["default_value"] = param.default_value
        export["user_param"] = param.is_user_param
        return export
        
    def _export_node(self, node, traverse_graph=True, export_connections=True):
        """
        """
        print "EXPORTING", node
        input_params = []
        for param in node._input_params.values():
            input_params.append(self._export_param(param,
                                        export_connections=export_connections))
        output_params = []
        for param in node._output_params.values():
            output_params.append(self._export_param(param,
                                        export_connections=export_connections))
        
        export = OrderedDict()
        
        export["name"] = node.name
        export["type"] = node.__class__.__name__
        export["input_params"] = input_params
        export["output_params"] = output_params
        if traverse_graph:
            export["nodegraph"] = self._export_graph(node.nodegraph)
        return export
        
    def _export_graph(self, graph, nodes=None):
        """
        """        
        sorted_nodes = []
    
        for node in graphing.topological_sort(graph):            
            sorted_nodes.append(self._export_node(node))            

        export = OrderedDict()

        if graph.output_node is None:
            export["output_node"] = None
        else:
            export["output_node"] = graph.output_node.name

        if nodes:
            sorted_nodes = filter(lambda x : x in nodes, sorted_nodes)
        
        export["nodes"] = sorted_nodes
        connections = self._export_connections(graph, nodes=nodes)
        export["connections"] = connections
        
        return export

    def _export_connections(self, graph, nodes=None):
        """
        @param graph NodeGraph to export connections from.
        @param nodes An optional list of Nodes. If specifed only connections related to those nodes
        will be exported.        
        """
        if nodes:
            connections = graph.connections.connections_between(nodes)
        else:            
            connections = graph.connections.all()

        connections_data = []
        for connection in connections:
            connection_data = {"src_node":connection.src_node.name,
                                "src_param":connection.src_param.name,
                                "dst_node":connection.dst_node.name,
                                "dst_param":connection.dst_param.name,
                                "passthru":connection.is_passthru}
            connections_data.append(connection_data)
        return connections_data

    def _export_node_type(self, node, type_name):
        """
        """
        export = OrderedDict()        
        export["type_name"] = type_name
        export["subtype"] = node.__class__.__name__        
        node_data = self._export_node(node, traverse_graph=True,
                                     export_connections=False)
        node_data["type"] = type_name        
        export["nodedef"] = node_data
        return export

    def export_graph(self, graph, nodes=None):
        """
        """
        return {"graph":self._export_graph(graph, nodes=nodes)}

    def export_node_type(self, node, type_name):
        """
        """
        return {"nodetype":self._export_node_type(node, type_name)}

    def _import_graph(self, graph_data, parent=None):
        """
        """
        if parent:
            graph = parent
        else:
            graph = NodeGraph()

        nodes = graph_data["nodes"]
        connections = graph_data["connections"]

        imported_nodes = []

        #for all nodes int the graph
        for node_data in nodes:
            #get the input/ouput param data
            import_params = node_data["input_params"]
            output_params = node_data["output_params"]            
        
            #import the node
            node = self._import_node(node_data, graph, import_params=True)

            #add the node and input/output param data to the list of import nodes
            imported_nodes.append((node, import_params, output_params))
        
        #run the list of imported nodes and import the params
        # for node, input_params, output_params in imported_nodes:
        #     for input_param_data in input_params:
        #         self._import_param(node, input_param_data, NodeParam.INPUT)
        #     for output_param_data in output_params:
        #         self._import_param(node, output_param_data, NodeParam.OUTPUT)

        for connection_data in connections:
            self._import_connnection(graph, connection_data)

        output_node = graph_data["output_node"]

        if output_node:
            output_node = graph.node(output_node)
        graph.output_node = output_node
        
        return graph

    def _import_node(self, node_data, graph, import_params=True, rename_duplicates=False):
        """
        """
        name = node_data["name"]
        node_type = node_data["type"]        
        #find a existing node with the same name
        node = graph.node(name)

        if node and rename_duplicates:


        if node is None:
            node = graph.add_node(name, node_type)

        if import_params:            
            for param_data in node_data["input_params"]:
                self._import_param(node, param_data, NodeParam.INPUT)
            for param_data in node_data["output_params"]:
                self._import_param(node, param_data, NodeParam.OUTPUT)
        
        self._import_graph(node_data["nodegraph"], parent=node.nodegraph)

        return node
                

    def _import_param(self, node, param_data, param_mode):
        """
        """
        name = param_data["name"]
        value = param_data["value"]
        reference = param_data["reference"]

        print "Importing Param:", node, name
        param_type = paramtype.NodeParamTypeRegistry.get(param_data["type"])        
        is_user_param = param_data["user_param"]
        default_value = param_data.get("default_value", NULL_VALUE)

        if param_mode == NodeParam.INPUT:
            if is_user_param:
                p = node.add_input_param(name, param_type, default_value=default_value)
            else:
                p = node.input_param(name)
        else:
            if is_user_param:
                p = node.add_output_param(name, param_type, default_value=default_value)
            else:
                p = node.output_param(name)        
        
        if not reference:
            p.value = value

    def _import_connnection(self, graph, connection_data):
        """
        """
        src_node_name = connection_data["src_node"]
        src_param_name = connection_data["src_param"]
        dst_node_name = connection_data["dst_node"]
        dst_param_name = connection_data["dst_param"]
        is_passthru = connection_data["passthru"]

        print "Importing Connection", src_node_name, src_param_name, dst_node_name, dst_param_name

        src_node = graph.node(src_node_name)
        src_param = src_node.find_param(src_param_name)
        if src_param is None:
            raise Exception("Unable to find param '%s' on node '%s'." % (src_param_name, src_node_name))
        src_param, mode = src_param

        dst_node = graph.node(dst_node_name)
        dst_param = dst_node.find_param(dst_param_name)
        if dst_param is None:
            raise Exception("Unable to find param '%s' on node '%s'." % (dst_param_name, dst_node_name))
        dst_param, mode = dst_param
        graph.connect(src_param, dst_param, passthru=is_passthru)


    def _import_node_type(self, node_type_data):
        """
        """
        type_name = node_type_data["type_name"]
        subtype = node_type_data["subtype"]
        subtype_class = NodeRegistry.get(subtype)        
        node_def = node_type_data["nodedef"]
        new_node_class = type(str(type_name), (subtype_class,), {"_NODE_DEF":node_def})
        return new_class

    def import_graph(self, graph_data):
        return self._import_graph(graph_data)

    def import_node_type(self, node_type_data):
        """
        """
        return self._import_node_type(node_type_data)

