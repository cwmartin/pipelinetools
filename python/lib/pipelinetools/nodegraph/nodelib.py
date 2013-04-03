
class NodeLibrary(object):
    """
    """
    
    def __init__(self):
        """
        """
        self._library_paths = []
        
    def add_library_path(self, path):
        """
        """
        pass
    
    def _load_library(self):
        """
        """
    
    @classmethod
    def get_node_type(cls, name):
        """
        """
        import opnode
        import node
        
        if hasattr(node, name):
            return getattr(node, name)
        if hasattr(opnode, name):
            return getattr(opnode, name)
        return None
    
    