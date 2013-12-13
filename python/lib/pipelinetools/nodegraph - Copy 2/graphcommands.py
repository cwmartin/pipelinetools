import commands
import registry
import nodegraphmodifier as ngm

def _get_unique_node_name(nodegraph, name):
        """
        """
        existing_node_names = [ n.name for n in nodegraph.nodes ]
        _name = name
        
        inc = 1
        while _name in existing_node_names:
            _name = "%s_%i" % (name, inc)
            inc += 1
        return _name

class AddNodeCommand(commands.Command):
    """
    """
    _COMMAND_NAME = "addnode"
    

    def _exexute(self, nodegraph, name, node_type):
        """
        """
        self._nodegraph = nodegraph
        node = self._modifier.add_node(nodegraph, name, node_type)
        self._node = weakref.ref(node)
        return node

    def _undo(self):
        """
        """
        self._modifier.remove_node(self._node())

class RemoveNodeCommand(commands.Command):
    """
    """
    _COMMAND_NAME = "removenode"
    
    def _execute(self, nodegraph, node):
        """
        """        
        self._nodegraph = nodegraph

        
        self._connections = []        

        for input_connection in node.input_connections():
            self._connection.append((weakref.ref(input_connection.src_param), 
                                    weakref.ref(input_connection.dstparam),
                                    input_connection.is_passthru))            

        for output_connection in node.output_connections():
            self._connections.append((weakref.ref(output_connection.src_param), 
                                    weakref.ref(output_connection.dstparam),
                                    output_connection.is_passthru))
        
        self._node = node        
        self._modifier.remove_node(node)

        """
        self._node_IO = registry.NodeGraphIOVersionRegistry.current_version()()
        self._node_export = self._node_IO._export_node(node)
        """

    def _undo(self):
        """
        """
        self._nodegraph._add_node(self._node)

        for connection in self._connections:
            self._modifier.connect(connection[0](), connection[1](), passthru=connection[2])            
        
        """
        node = self._node_IO._import_node(self._node_export, self._nodegraph)
        """        

class ReparentNodeCommand(commands.Command):
    """
    """
    _COMMAND_NAME = "reparentnode"
    
    def _execute(self, node, parent):
        """
        """
        self._old_parent = node.parent_graph
        self._modifier.reparent_node(node, name)


class RenameNodeCommand(commands.Command):
    """
    """
    _COMMAND_NAME = "renamenode"
    pass

class ConnectCommand(commands.Command):
    """
    """
    _COMMAND_NAME = "connect"

    def _execute(self, src_param, dst_param, passthru=False):
        """
        """
        self._src_param = weakref.ref(src_param)
        self._dst_param = weakref.ref(dst_param)        
        self._graph = wearkref.ref(self._session._curr_graph)        
        self._session._curr_graph.connect(src_param, dst_param, passthru=passthru)

    def _undo(self):
        """
        """
        self._graph().disconnect(self._src_param(), self._dst_param())

class DisconnectCommand(Command):
    """
    """
    _COMMAND_NAME = "disconnect"

    def _execute(self, src_param, dst_param):
        """
        """
        self._src_param = weakref.ref(src_param)
        self._dst_param = weakref.ref(dst_param)                
        self._graph = wearkref.ref(self._session._curr_graph)

        connections = self._session._curr_graph.list_connections(src_param=src_param,
            dst_param=dst_param)

        if connections is None:
            raise commands.CommandExecuteError("Connection between '%s' and '%s' does not exist." 
                    % (src_param, dst_param))
        connection = connections[0]
        self._passthru = connection.is_passthru
    
    def _undo(self):
        """
        """
        self._graph.connect(self._src_param, self._dst_param, passthru=self._passthru)
