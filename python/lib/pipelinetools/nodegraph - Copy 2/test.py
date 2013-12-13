import os
import sys
import platform

sys.setrecursionlimit(100)

#from node import Node

import session

from node import NodeGraph
from opnode import OperatorNode, EchoOperator, CodeOperator
from paramtype import VariantType

ng = NodeGraph()

op1 = ng.add_node("op1", "OperatorNode")
op2 = ng.add_node("op2", "EchoOperator")
op3 = ng.add_node("op3", "CodeOperator")
op4 = ng.add_node("op4", "OperatorNode")

#op1.add_input_param("user_param1", VariantType)
op3.add_input_param("user_param1", VariantType)

op1.output_param("netout").value = "HELLO WORLD"

ng.connect(op1.output_param("netout"), op2.input_param("echo"))
ng.connect(op1.output_param("netout"), op3.input_param("netin"))
ng.connect(op1.output_param("netout"), op3.input_param("user_param1"))

code = """
print "this is the Code node"
a = 10 + 1
print inputs["user_param1"].value

out = inputs["user_param1"].value

outputs["return"].value = a
"""
op3.input_param("code").value = code

ng.connect(op3.output_param("return"), op2.input_param("echo"))
ng.connect(op2.output_param("netout"), op4.input_param("netin"))

ng.output_node = op4

subgraphnode = ng.collapse(nodes=[op2, op3])

ng.connect(op1.output_param("netout"), op3.input_param("user_param1"))

import writer
if platform.system() == "Linux":
    export_path = "/home/christopher/dev/scratch"
else:
    export_path = "D:/dev/"
compress = False
writer.NodeGraphWriter.write(ng, os.path.join(export_path, "test.smg"), compress=compress)
writer.NodeTypeWriter.write(subgraphnode, "MyNodeType2", os.path.join(export_path, 
                    "test.nte"), compress=compress)

import session
print op3.parent_node

s = session.Session(graph=ng)
print s.get_path(op3)

print s.node(".//subgraph/op3")
