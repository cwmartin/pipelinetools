import json
import writer
import opnode

graph = writer.NodeGraphReader.read(r"D:\dev\test.smg")

print "-->", graph.node("subgraph").nodegraph.node("op2").input_param("echo")
print "-->", graph.node("subgraph").nodegraph.node("op3").output_param("return")
print "------------->", graph.node("subgraph")._evaluate()


#for node in graph.nodes:
#    print node

from nodegraph import NodeGraphExecutor
nge = NodeGraphExecutor()
nge.execute(graph)
