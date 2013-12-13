"""
"""
import networkx

def _nodegraph_to_networkx(graph):
    """
    """    
    nx_graph = networkx.MultiDiGraph()
    for node in graph.nodes:        
        nx_graph.add_node(node)        
    for connection in graph.connections.all():    
        nx_graph.add_edge(connection.src_node, connection.dst_node)
    return nx_graph

def topological_sort(graph):
    """
    """
    nx_graph = _nodegraph_to_networkx(graph)    
    sorted_nodes = networkx.topological_sort(nx_graph)    
    return sorted_nodes

def cycle_test(graph):
    """
    """
    nx_graph = _nodegraph_to_networkx(graph)
    return networkx.simple_cycles(nx_graph)




