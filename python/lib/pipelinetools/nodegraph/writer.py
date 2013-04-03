import json
import exporter
import gzip

class GraphWriter(object):
    """
    """
    def write(self, graph, path, compress=True):
        """
        """
        exp = exporter.GraphExporter()
        export_data = exp.export(graph)                
        header = {"version":exp.VERSION}        
        output = {"header":header,
                "data":export_data}

        if compress:
            f = gzip.open(path, "wb")
        else:
            f = open(path, "w")

        json.dump(output, f, indent=4)
        f.close()

class NodeTypeWriter(object):
    """
    """
    def write(self, node, typename, path, compress=True):
        """
        """
        exp = exporter.NodeTypeExporter()
        export_data = exp.export(node, typename)        
        header = {"version":exp.VERSION}

        output = {"header":header,
                "data":export_data}              

        if compress:  
            f = gzip.open(path, "wb")
        else:
            f = open(path, "w")

        json.dump(output, f, indent=4)
        f.close()
