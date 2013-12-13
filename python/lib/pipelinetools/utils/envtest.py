import sys
from pipelinetools.utils import environment

if __name__ == "__main__":

    env = environment.Environment(env={})

    env.set("VALUE1", "value1:::value5")
    #env.list()
    env.append("VALUE1", "value2:")
    #env.list()
    env.prepend("VALUE1", "value0")
    #key_values = env.list(out=sys.stdout)

    print env.expandvars("${VALUE0}/${VALUE1}")