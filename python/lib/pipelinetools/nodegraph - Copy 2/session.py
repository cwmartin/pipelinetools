import os
import sys

import registry
import nodegraph
# TODO: The below are needed to init the registry. Should be moved to be dynamic
import node
import opnode
import paramtype
import nodegraphpath

class Session(object):
    """
    """

    _instance = None

    def __new__(self, *args, **kwargs):
        """
        """
        if not cls._instance:
            cls._instance = user()

    def __init__(self, graph=None):
        """
        """
        if graph is None:
            graph = nodegraph.NodeGraph()

        self._root_graph = graph

        self._curr_graph = self._root_graph

    def get_path(self, node):
        """
        """
        return nodegraphpath.get_path(node)

    def node(self, path):
        """
        """
        return nodegraphpath.get_node(path, self._curr_graph, self._root_graph)









