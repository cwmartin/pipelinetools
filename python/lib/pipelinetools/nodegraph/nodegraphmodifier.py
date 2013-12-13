"""
"""

import registry

class NodeGraphModifier(object):
    """
    """

    def _get_unique_node_name(self, nodegraph, name):
        """
        """
        existing_node_names = [ n.name for n in nodegraph.nodes ]
        _name = name
        
        inc = 1
        while _name in existing_node_names:
            _name = "%s_%i" % (name, inc)
            inc += 1
        return _name

    def add_node(self, nodegraph, name, node_type):
        """
        """
        node_type = registry.NodeRegistry.get(node_type)
        node_name = self._get_unique_node_name(nodegraph, name)
        node = node_type(node_name, parent=nodegraph)
        nodegraph._add_node(node)
        return node

    def remove_node(self, node):
        """
        """
        nodegraph = node.parent_graph
        connections = node.connections()


        for src_param, dst_param in node.input_connections():
            self.disconnect(nodegraph, src_param, dst_param)

        for src_param, dst_param in node.output_connections():
            self.disconnect(nodegraph, src_param, dst_param)

        node._parent = None
        self.nodes.remove(node)

    def rename_node(self, node, name):
        """
        """
        new_name = self._get_unique_node_name(nod, name)
        node._name = new_name        

    def reparent_node(self, nodes, parent):
        """
        """
        if nodes and nodes isinstance(node, (list, tuple)):            
            nodegraph = nodes[0].parent_graph
            if filter(lambda x : x.parent_graph != nodegraph, nodes):
                raise Exception("Unable to reparent sets of nodes of differing parent nodegraphs.")

            inner_connections = nodegraph.connections.connections_between(nodes)
            connections_to_remove = []

            for node in nodes:
                connections_to_remove.extend(node.connections(src=True, dst=True))

            connections_to_remove = filter(lambda x : x not in inner_connections, connections_to_remove)

            for inner_connection in inner_connections:
                parent.connections._add(inner_connection)        
        else:
            connections_to_remove = node.connections(src=True, dst=True)

        node.parent_graph.connections.remove(connections_to_remove)        

        for node in nodes:
            nodegraph.nodes.remove(node)            
            parent._add_node(node)            

    def reparent_node(self, nodes, parent):
        """
        """
        if nodes and nodes isinstance(node, (list, tuple)):            
            nodegraph = nodes[0].parent_graph
            if filter(lambda x : x.parent_graph != nodegraph, nodes):
                raise Exception("Unable to reparent sets of nodes of differing parent nodegraphs.")
        else:
            nodegraph = node.parent_graph
            nodes = [nodes]

        graphIO = registry.NodeGraphIOVersionRegistry.current_version()()

        graph_export = graphIO.export_graph(nodegraph, nodes=nodes)

        graphIO.import_graph(graph_export, parent=nodegraph, rename_duplicates=True)


    def connect(self, src_param, dst_param, passthru=False):
        """
        """
        if passthru:
            nodegraph = src_param.node.parent_graph
            if nodegraph != dst_param.node.parent_graph:
                raise Exception("Cannot connect params accross nodegraphs.")
            conn = nodegraph.connections.add(src_param, dst_param)
        else:
            nodegraph = dst_param.node.parent_graph
            conn = nodegraph.connections.add_passthru(src_param, dst_param)
        return conn

    def disconnect(self, src_param, dst_param):
        """
        """
        nodegraph = dst_param.node.parent_graph
        conns = nodegraph.connections.find(src_param=src_param, dst_param=dst_param,
            ignore_passthru=False)
        if conns:
            nodegraph.connections.remove(conns)