
code = """

print "-->", inputs["blarg"]

"""

ccode = compile(code, "<string>", "exec")

__inputs = {"blarg":"YAY"}

exec(ccode, {"inputs":__inputs})