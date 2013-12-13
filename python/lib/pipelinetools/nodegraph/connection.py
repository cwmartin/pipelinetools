"""
"""

class NodeGraphConnection(object):
    """
    """
    def __init__(self, src_param, dst_param, is_passthru=False):
        """
        """

        self._src_param = src_param
        self._dst_param = dst_param
        self._is_passthru = is_passthru

    @property
    def src_param(self):
        """
        """
        return self._src_param

    @property
    def src_node(self):
        """
        """
        return self.src_param.node

    @property
    def dst_param(self):
        """
        """
        return self._dst_param

    @property
    def dst_node(self):
        """
        """
        return self.dst_param.node

    @property
    def is_passthru(self):
        """
        """
        return self._is_passthru

    def __str__(self):
        """
        """
        return "%s->%s" % (self.src_param, self.dst_param)

    def __repr__(self):
        """
        """
        return self.__str__()

class NodeGraphConnections(object):
    """
    """
    def __init__(self):
        """
        """
        self._connections = []

    def add(self, src_param, dst_param):
        """
        """
        conn = NodeGraphConnection(src_param, dst_param)
        self._add(conn)
        return conn

    def add_passthru(self, src_param, dst_param):
        """
        """
        conn = NodeGraphConnection(src_param, dst_param, is_passthru=True)
        self._add(conn)
        return conn

    def _add(self, connection):
        """
        """
        self._connections.append(connection)

    def remove(self, connections):
        """
        """
        if not isinstance(connections, (list, tuple)):
            connections = [connections]

        for connection in connections:
            if connection in self._connections:                
                self._connections.remove(connection)

    def pop(self, connections):
        """
        """
        if not isinstance(connections, (list, tuple)):
            connections = [connections]

        popped = []
        for connection in connections:
            if connection in self._connections:
                idx = self._connections.index(connection)
                popped.append(self._connections.pop(idx))
        return popped

    def find(self, src_node=None, src_param=None, dst_node=None, dst_param=None,
            ignore_passthru=True):
        """
        """
        conns = []

        if src_node or src_param or dst_node or dst_param:
            for conn in self._connections:
                if conn._is_passthru and ignore_passthru:
                    continue
                if src_node:
                    if src_node != conn.src_node:
                        continue
                if src_param:
                    if src_param != conn.src_param:
                        continue
                if dst_node:
                    if dst_node != conn.dst_node:
                        continue
                if dst_param:
                    if dst_param != conn.dst_param:
                        continue
                conns.append(conn)
        return conns

    def all(self, ignore_passthru=True):
        """
        """
        conns = []
        for conn in self._connections:
            if not conn.is_passthru:
                conns.append(conn)
        return conns

    def connections_between(self, nodes):
        """
        Find all connections between the nodes specified by nodes.
        if a connection exists to a node not in nodes, reject it.
        """
        keep = []
        for node in nodes:
            #find connections where node is a src
            src_conns = self.find(src_node=node)
            #find connections where node is a dst
            dst_conns = self.find(dst_node=node)

            for src_conn in src_conns:
                if src_conn.dst_node in nodes:
                    keep.append(src_conn)
            for dst_conn in dst_conns:
                if dst_conn.src_node in nodes:
                    keep.append(dst_conn)
        return list(set(keep))