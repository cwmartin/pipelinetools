import json
import gzip
import exporter
from registry import NodeGraphIOVersionRegistry



class NodeGraphWriter(object):
    """
    """
    @classmethod
    def write(cls, graph, path, compress=True):
        """
        """
        graph_io = NodeGraphIOVersionRegistry.current_version()()
        export_data = graph_io.export_graph(graph)
        header = {"version":graph_io.VERSION}
        output = {"header":header, "data":export_data}

        if compress:

            f = gzip.open("%s.gz" % path, "wb")
        else:
            f = open(path, "w")

        json.dump(output, f, indent=4)
        f.close()

class NodeGraphReader(object):
    """
    """
    @classmethod
    def read(cls, path):
        """
        """
        if path.endswith(".gz"):
            f = gzip.open(path, "rb")
        else:
            f = open(path, "r")

        read_data = json.load(f)
        header = read_data["header"]
        version = header["version"]
        data = read_data["data"]
        graph_data = data["graph"]
        
        graph_io_class = NodeGraphIOVersionRegistry.get(version)
        graph_io = graph_io_class()

        graph = graph_io.import_graph(graph_data)

        return graph

class NodeTypeWriter(object):
    """
    """
    @classmethod
    def write(cls, node, type_name, path, compress=True):
        """
        """
        graph_io = NodeGraphIOVersionRegistry.current_version()()
        export_data = graph_io.export_node_type(node, type_name)        
        header = {"version":graph_io.VERSION}
        output = {"header":header,
                "data":export_data}              

        if compress:  
            f = gzip.open(path, "wb")
        else:
            f = open(path, "w")

        json.dump(output, f, indent=4)
        f.close()

class NodeTypeReader(object):
    """
    """
    @classmethod
    def read(cls, path):
        """
        """
        pass