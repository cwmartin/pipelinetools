import json
from nodegraph import NodeGraph
from nodeparam import NodeParam 
from nodeparam import NULL_VALUE
from registry import NodeGraphIOVersionRegistry
import paramtype
import nodelib
from pipelinetools.utils.ordereddict import OrderedDict

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
        if param.has_referenced_value():                  
            if export_connections:  
                value = param.referenced_value()
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
        
    def _export_graph(self, graph):
        """
        """
        nodes = []
        for node in graph.nodes:
            print "exporting", node
            nodes.append(self._export_node(node))            
        export = OrderedDict()                
        if graph.output_node is None:            
            export["output_node"] = None
        else:
            export["output_node"] = graph.output_node.name
        export["nodes"] = nodes
        return export

    def _export_node_type(self, node, type_name):
        """
        """
        export = OrderedDict()        
        export["type_name"] = type_name
        export["subtype"] = node.__class__.__name__
        #nodegraph_data = self._export_graph(node.nodegraph)
        #node_data = exp._export_node(node, traverse_graph=False,
        #                           export_connections=False)
        #node_data["nodegraph"] = nodegraph_data
        
        node_data = self._export_node(node, traverse_graph=True,
                                     export_connections=False)
        node_data["type"] = type_name        
        export["nodedef"] = node_data
        return export

    def export_graph(self, graph):
        """
        """
        return {"graph":self._export_graph(graph)}

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

        imported_nodes = []

        for node_data in nodes:
            import_params = node_data["input_params"]
            output_params = node_data["output_params"]            
        
            node = self._import_node(node_data, graph, import_params=False)

            imported_nodes.append((node, import_params, output_params))

            

        for node, input_params, output_params in imported_nodes:
            for input_param_data in input_params:
                self._import_param(node, input_param_data, NodeParam.INPUT)
            for output_param_data in output_params:
                self._import_param(node, output_param_data, NodeParam.OUTPUT)

        output_node = graph_data["output_node"]

        if output_node:
            output_node = graph.node(output_node)
        graph.output_node = output_node
        
        return graph

    def _import_node(self, node_data, graph, import_params=True):
        """
        """
        name = node_data["name"]
        node_type = node_data["type"]

        node = graph.add_node(name, node_type)
        
        self._import_graph(node_data["nodegraph"], parent=node.nodegraph)
        
        if import_params:
            for param_data in node_data["input_params"]:
                self._import_param(node, param_data, NodeParam.INPUT)
            for param_data in node_data["output_params"]:
                self._import_param(node, param_data, NodeParam.OUTPUT)

        return node

    def _import_param(self, node, param_data, param_mode):
        """
        """
        name = param_data["name"]
        param_type = paramtype.NodeParamTypeRegistry.get(param_data["type"])
        value = param_data["value"]
        is_reference = param_data["reference"]
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

        if is_reference:
            ref_node_name, ref_param_name = value.split(".")
            ref_node = node.parent.node(ref_node_name)
            ref_param = ref_node.output_param(ref_param_name)
            p.value = ref_param
        else:
            p.value = value

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

