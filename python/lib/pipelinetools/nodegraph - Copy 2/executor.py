import graphing

class CycleError(Exception):pass

class NodeGraphExecutor(object):
    """
    """

    def __init__(self):
        """
        """
        self.executed = []

    def execute(self, nodegraph):
        """
        """
        output_node = nodegraph.output_node
        #check for a cycle in the graph
        cycles = graphing.cycle_test(nodegraph)
        if cycles:
            raise CycleError("Cycle exists between node '%s' "\
                             "and node '%s'." % (cycles[0][0], cycles[0][1]))
        #traverse the graph start from the output node
        self._traverse(output_node)

    def _traverse(self, node):
        """
        """
        while True:
            #get an incoming node
            next_node = node._evaluate(self)
            #if no incoming nodes
            if next_node is None:
                break
            #traverse to that node
            self._traverse(next_node)
        node._execute(self)
