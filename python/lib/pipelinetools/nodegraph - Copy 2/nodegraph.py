        


class NodeGraph(object):
    """
    """
    def __init__(self, parent_node=None):
        """
        """
        self._parent_node = parent_node
        self._output_node = None
        self._nodes = []
        self._node_connections = connections.NodeGraphConnections()

    @property
    def parent_node(self):
        """
        """
        return self._parent_node

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
        return self._nodes

    @property
    def connections(self):
        """
        """
        return self._node_connections

    def list_connections(self, src_node=None, src_param=None, dst_node=None,
        dst_param=None, ignore_passthru=True):
        """
        """
        return self.connections.find(src_node=src_node, src_param=src_param,
            dst_node=dst_node, dst_param=dst_param, ignore_passthru=ignore_passthru)

    def node(self, name):
        """
        """
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def _add_node(self, node):
        """
        """
        node._parent_graph = self
        self._nodes.append(node)
            
    def connect(self, src_param, dst_param, passthru=False):
        """
        Connect two node params.
        @param src_param The source param.
        @param dst_param The destination param.
        """

        if not passthru:
            if src_param.node.parent_graph != dst_param.node.parent_graph:
                raise Exception("Unable to connect '%s' to '%s'. Cannot connect parameters accross "\
                    "graphs." % (src_param, dst_param))

        existing_cons = self._node_connections.find(dst_param=dst_param)
        if existing_cons:
            for existing_con in existing_cons:
                self.disconnect(existing_con.src_param, existing_con.dst_param)
                #self._node_connections.remove(existing_con)

        if passthru:
            conn = self._node_connections.add_passthru(src_param, dst_param)
        else:
            conn = self._node_connections.add(src_param, dst_param)

        dst_param._value = weakref.ref(src_param)


    def disconnect(self, src_param, dst_param):
        """
        Disconnect two node params.
        @param src_param The source param.
        @param dst_param The destination param.
        """
        conn = self._node_connections.find(src_param=src_param, dst_param=dst_param)
        if conn:
            self._node_connections.remove(conn)
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

        subgraph_node = self.add_node("subgraph", "SubgraphNode")

        subgraph_input_node = subgraph_node.child_node("input")
        subgraph_output_node = subgraph_node.child_node("output")

        subgraph_node.nodegraph.output_node = subgraph_output_node

        if nodes:
            for node in nodes:
                self.move_node(node, subgraph_node.nodegraph)

            conns = self.connections.connections_between(nodes)

            #pop the connections from the current nodegraph and move them
            #into the subgraph's nodegraph
            self.connections.pop(conns)
            for conn in conns:
                subgraph_node.nodegraph._node_connections._add(conn)

            reconnect_input_params = []
            reconnect_output_params = []

            #for each node in the subgraph
            for node in nodes:
                #for each of the node intput connections
                for input_connection in node.input_connections():

                    #if the connection is internal to the subgraph
                    if input_connection.src_node in nodes:
                        #don't worry about it
                        continue

                    #reroute that connection through the subgraphs "input" node

                    print "Rerouting Input Connections..."
                    dst_param = input_connection.dst_param
                    src_param = input_connection.src_param

                    self.disconnect(src_param, dst_param)

                    print "Rerouting:", src_param, dst_param

                    #create a new input on the subgraph node
                    new_input_param = subgraph_node.add_input_param(dst_param.name,
                        dst_param.type, default_value=dst_param.default_value)
                    print "Creating new subgraph node input", new_input_param


                    #create a new output param in the "input" node
                    new_output_param = subgraph_input_node.add_output_param(dst_param.name,
                        dst_param.type, default_value=dst_param.default_value)
                    print "Creating new subgraph input node output param", new_output_param

                    #connect the new subgraph input param to the origianl src param
                    self.connect(src_param, new_input_param)
                    print "Connecting", src_param, new_input_param

                    #connect the "input" node's output param to the subraph nodes input param
                    subgraph_node.nodegraph.connect(new_input_param, new_output_param,
                        passthru=True)
                    print "Connecting passthru", new_input_param, new_output_param

                    #connect the original input param to the output of the "input" node
                    subgraph_node.nodegraph.connect(new_output_param, dst_param)
                    print "Connect", new_output_param, dst_param

                for output_connection in node.output_connections():
                    #if the connection is internal to the subgraph
                    if output_connection.dst_node in nodes:
                        #don't worry about it
                        continue

                    #reroute the connection through the subgraph "output" node
                    print "Rerouting Output Connections..."
                    src_param = output_connection.src_param
                    dst_param = output_connection.dst_param

                    self.disconnect(src_param, dst_param)

                    print "Rerouting:", src_param, dst_param

                    #create a new output param on the subgraph node
                    new_output_param = subgraph_node.add_output_param(src_param.name,
                        src_param.type, default_value=src_param.default_value)
                    print "Creating new subgraph output param", new_output_param

                    #create a new input param on the "output" node
                    new_input_param = subgraph_output_node.add_input_param(src_param.name,
                        src_param.type, default_value=src_param.default_value)
                    print "Creating new subgraph output node input param", new_input_param

                    #connect the "output" nodes input to the original node's output
                    subgraph_node.nodegraph.connect(src_param, new_input_param)
                    print "Connecting", src_param, new_input_param

                    #connect the subgraph's new output param to the "output" nodes' input param
                    subgraph_node.nodegraph.connect(new_input_param, new_output_param,
                        passthru=True)
                    print "Connecting passthru", new_input_param, new_output_param

                    #connect the orignal dest param to the subgraph's new output param
                    self.connect(new_output_param, dst_param)
                    print "Connecting", new_output_param, dst_param

        return subgraph_node

