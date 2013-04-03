import json
import reader

f = open(r"D:\dev\test.json", "r")
data = json.load(f)
f.close()

nr = reader.NodeReader()
g = nr._import_graph(data)

#output_node = g.node("op2")
#subgraph = g.node("subgraph")
#suboutput = subgraph.nodegraph.node("output")
#subgraph.nodegraph.output_node = suboutput
#g.output_node = output_node
#g._execute()

subgraph = g.node("subgraph")

import writer

ntw = writer.NodeTypeWriter()
type_data = ntw.export_type(subgraph, "BlargType")
print json.dumps(type_data, indent=4)

ntr = reader.NodeTypeReader()
ntr.import_type(type_data)

"""
import networkx as nx
import matplotlib.pyplot as plt
nx.draw_circular(g.graph)
plt.show()
"""

