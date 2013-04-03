from pipelinetools.utils.ordereddict import OrderedDict
import json

class Exporter(object):
    """
    """    
    VERSION = None

    def export(self, *args, **kwargs):
        """
        """                
        export_data = self._export(*args, **kwargs)
        return export_data        

    def _export(self, *args, **kwargs):
        """
        """
        pass

class NodeTypeExporter(Exporter):
    """
    """
    
    VERSION = 1
    
    def _export_node_type(self, node, typename):
        """        
        """
        export = OrderedDict()        
        export["typename"] = typename
        export["subtype"] = node.__class__.__name__        
        exp = GraphExporter()        
        nodegraph_data = exp._export_graph(node.nodegraph)
        node_data = exp._export_node(node, traverse_graph=False,
                                     export_connections=False)
        node_data["nodegraph"] = nodegraph_data                                        
        export["node"] = node_data
        return export
    
    def _export(self, node, typename):
        """
        """
        return {"nodetype":self._export_node_type(node, typename)}

class GraphExporter(Exporter):
    """
    """
    
    VERSION = 1
    
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
            nodes.append(self._export_node(node))            
        export = OrderedDict()                
        if graph.output_node is None:            
            export["output_node"] = None
        else:
            export["output_node"] = graph.output_node.name
        export["nodes"] = nodes
        return export
    
    def _export(self, graph):
        """    
        """
        return {"graph":self._export_graph(graph)}