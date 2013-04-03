#from node import Node
import networkx as nx
from nodegraph import NodeGraph
from nodegraph import NodeGraphExecutor
from opnode import OperatorNode, EchoOperator, CodeOperator
from paramtype import VariantType

ng = NodeGraph()

op1 = ng.add_node("op1", "Node")
op2 = ng.add_node("op2", "Node")
op3 = ng.add_node("op3", "SwitchNode")
op4 = ng.add_node("op4", "Node")
op5 = ng.add_node("op5", "Node")
op6 = ng.add_node("op6", "Node")

op4.add_input_param("user_param1", VariantType)

op4.input_param("netin").value = op1.output_param("netout")
op4.input_param("user_param1").value = op3.output_param("chosen_value")

op3.input_param("index_0").value = op2.output_param("netout")
op3.add_input_param("index_1", VariantType)
op3.input_param("index_1").value = op5.output_param("netout")

op3.input_param("switch_index").value = 0

#op6.input_param("netin").value = op1.output_param("netout")
#op1.input_param("netin").value = op6.output_param("netout")
ng.output_node = op4


#ng._execute()

for node in ng.nodes:
    print node, node.input_connections()

#print "-->", nx.simple_cycles(ng.graph)



import writer
import json

nw = writer.NodeWriter()
#export_g = nw.export_node(subgraphnode)
export_g = nw.export_graph(ng)
d = json.dumps(export_g, indent=4)

f = open(r"D:\dev\test.json", "w")
f.write(d)
f.close()


print "Done"