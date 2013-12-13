from nodegraph import NodeGraph
from nodeparam import NodeParam 
from nodeparam import NULL_VALUE
import paramtype
import nodelib
import json

class NodeTypeReader(object):
    """
    """
    def _read_type(self, data):        
        typename = data["typename"]
        subtype = data["subtype"]
        version = data["version"]
        subtype = nodelib.NodeLibrary.get_node_type(subtype)    
        new_class = type(str(typename), (subtype,), {})
        
        return new_class

    def read(self, data):
        """
        """
        return self._read_type(data)


class JSONNodeTypeReader(NodeTypeReader):
    """
    """
    def read(self, filename):
        """
        """        
        fp = open(filename, "r")
        data = json.load(fp)        
        fp.close()
        return super(JSONNodeTypeReader, self).read(data)
        
class NodeReader(object):
    """
    """
    def _reader_param(self, node, data, mode):
        """
        """
        name = data["name"]
        ptype = data["type"]
        ptype = getattr(paramtype, ptype)
        value = data["value"]
        is_reference = data["reference"]
        is_user_param = data["user_param"]
        default_value = data.get("default_value", NULL_VALUE)
        
        if mode == NodeParam.INPUT:
            if is_user_param:
                p = node.add_input_param(name, ptype, default_value=default_value)
            else:
                p = node.input_param(name)
        else:
            if is_user_param:
                p = node.add_output_param(name, ptype, default_value=default_value)
            else:
                p = node.output_param(name)
                
        if is_reference:
            ref_node_name, ref_param_name = value.split(".")
            ref_node = node.parent.node(ref_node_name)
            ref_param = ref_node.output_param(ref_param_name)
            p.value = ref_param
        else:
            p.value = value 
            
    def _read_node(self, data, graph):
        """
        """
        
        name = data["name"]
        ntype = data["type"]
        
        node = graph.add_node(name, ntype)
        
        for param_data in data["input_params"]:            
            self._read_param(node, param_data, NodeParam.INPUT)
        
        for param_data in data["output_params"]:            
            self._read_param(node, param_data, NodeParam.OUTPUT)
            
        self._read_graph(data["nodegraph"], parent=node.nodegraph)
        
    def _read_graph(self, data, parent=None):
        """
        """   
        if parent:     
            graph = parent
        else:
            graph = NodeGraph()
        
        nodes = data["nodes"]
        for node in nodes:
            self._read_node(node, graph)
        
        output_node = data["output_node"]
        if output_node:
            output_node = graph.node(output_node)        
        graph.output_node = output_node
        return graph

            