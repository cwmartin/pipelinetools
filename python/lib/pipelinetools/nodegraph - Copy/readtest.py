import json
import writer
import opnode

graph = writer.NodeGraphReader.read(r"D:\dev\test.smg")

print graph.node("subgraph").nodegraph.node("op2").input_param("echo").value

#for node in graph.nodes:
#    print node

# from nodegraph import NodeGraphExecutor
# nge = NodeGraphExecutor()
# nge.execute(graph)
