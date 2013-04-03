from ordereddict import OrderedDict


def export_node_type(self, subgraph, typename):
        """
        """
        node_data = self.export_node(subgraph)
        node_data["type"] = typename
        node_data["subtype"] = subgraph.__class__.__name__
        return node_data
    
    
class NodeWriter(object):
    """
    """
        
    def _export_param(self, param):
        """
        """
        if param.has_referenced_value():            
            value = param.referenced_value()
            value = str(value)
            reference = True
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
        
    def _export_node(self, node):
        """
        """
        input_params = []
        for param in node._input_params.values():
            input_params.append(self._export_param(param))
        output_params = []
        for param in node._output_params.values():
            output_params.append(self._export_param(param))
        
        export = OrderedDict()
        
        export["name"] = node.name
        export["type"] = node.__class__.__name__
        export["input_params"] = input_params
        export["output_params"] = output_params
        export["nodegraph"] = self._export_graph(node.nodegraph)
                        
        return export
        
    def _export_graph(self, graph):
        """
        """
        nodes = []
        for node in graph.nodes:                    
            nodes.append(self._export_node(node))
            
        export = OrderedDict()        
        if graph.output_node is None:            
            export["output_node"] = None
        else:
            export["output_node"] = graph.output_node.name
        export["nodes"] = nodes
        return export
    
    def export_node(self, node):
        """
        """
        return self._export_node(node)
    
    def export_graph(self, graph):
        """
        """
        return self._export_graph(graph)
    
    def export_node_type(self, subgraph, typename):
        """
        """
        node_data = self.export_node(subgraph)
        node_data["type"] = typename
        node_data["subtype"] = subgraph.__class__.__name__
        return node_data
        
class JSONNodeWriter(NodeWriter):
    """        
    """
        