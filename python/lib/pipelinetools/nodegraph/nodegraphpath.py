
class NodeGraphPathError(Exception):pass

def get_path(node):
    """
    """
    path_list = []
    curr_node = node        
    while curr_node:            
        path_list.append(curr_node.name)            
        curr_node = curr_node.parent_node
    return "/%s" % "/".join(reversed(path_list))

def get_node(path, graph, root_graph):
    """
    """
    path_list = path.split("/")
    curr_graph = graph    
    while path_list:
        node_name = path_list.pop(0)
        if node_name == "":
            curr_graph = root_graph
            continue
        if node_name == ".":
            continue
        if node_name == "..":            
            try:
                curr_graph = curr_graph.parent_node.parent_graph
                continue
            except:
                raise NodeGraphPathError("Path '%s' does not exist." % path)                
            
        node = curr_graph.node(node_name)
        if node is None:
            raise NodeGraphPathError("Unable to find node '%s' in node path '%s'." % (node_name, path))                
        curr_graph = node.nodegraph
    return node