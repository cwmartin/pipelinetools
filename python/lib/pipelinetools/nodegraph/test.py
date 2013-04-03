import os
import platform

#from node import Node
from node import NodeGraph
from opnode import OperatorNode, EchoOperator, CodeOperator
from paramtype import VariantType

ng = NodeGraph()

op1 = ng.add_node("op1", "OperatorNode")
op2 = ng.add_node("op2", "EchoOperator")
op3 = ng.add_node("op3", "CodeOperator")
op4 = ng.add_node("op4", "OperatorNode")

op1.add_input_param("user_param1", VariantType)
op3.add_input_param("user_param1", VariantType)

op1.output_param("netout").value = "HELLO WORLD"
op2.input_param("echo").value = op1.output_param("netout")
op3.input_param("netin").value = op1.output_param("netout")

op3.input_param("user_param1").value = op1.output_param("netout")


code = """
print "this is the Code node"
a = 10 + 1
print inputs["user_param1"].value

out = inputs["user_param1"].value

outputs["return"].value = a
"""
op3.input_param("code").value = code


op2.input_param("echo").value = op3.output_param("return")
op4.input_param("netin").value = op2.output_param("netout")

ng.output_node = op4

from nodegraph import NodeGraphExecutor
nge = NodeGraphExecutor()
nge.execute(ng)

subgraphnode = ng.collapse(nodes=[op2, op3])

import writer

graph_writer = writer.GraphWriter()

if platform.system() == "Linux":
    export_path = "/home/christopher/dev/scratch"
else:
    export_path = "D:/dev/"

compress = False
graph_writer.write(ng, os.path.join(export_path, "test.smg"), compress=compress)
node_type_writer = writer.NodeTypeWriter()
node_type_writer.write(subgraphnode, "MyNodeType2", os.path.join(export_path, 
                    "test.nte"), compress=compress)

#import reader

#r = reader.JSONNodeTypeReader()

#print r.read(os.path.join(export_path, "test.nte"))

