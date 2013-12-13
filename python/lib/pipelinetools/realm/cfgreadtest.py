import os
import sys
import json
import re
import pipelinetools.utils.environment as environment
import platform


def remove_comments(string):
    """
    """
    string = re.sub(re.compile("/\*.*?\*/", re.DOTALL), "", string)
    string = re.sub(re.compile("//.*?\n"), "", string)
    return string

f = open("testconfig.json", "r")
json_text = f.read()
json_text = remove_comments(json_text)

#print json_text
t = json.loads(json_text)



class Parser(object):
    """
    """
    def __init__(self, env=None):
        """
        """
        if env is None:
            self.env = environment.Environment(env={})
        else:
            self.env = env

    def parse_env_block(self, env_block):
        """
        """
        for key, val in env_block.items():
            if isinstance(val, dict):
                for val_key, val_val in val.items():
                    if val_key == "prepend":
                        self.env.prepend(key, val_val)
                    elif val_key == "append":
                        self.env.append(key, val_val)
                    else:
                        raise Exception(val_key)
            else:
                self.env.set(key, val)

    def parse_version(self, version_name, version_data):
        """
        """
        if version_name == "common":
            self.parse_env_block(version_data)
        else:
            if "common" in version_data:
                self.parse_env_block(version_data["common"])
            system_name = platform.system().lower()
            if system_name in version_data:
                self.parse_env_block(version_data[system_name])

    def parse(self, data):
        """
        """
        common_env = data["environment"]
        latest = data["latest"]
        versions = data["versions"]

        self.parse_env_block(common_env)

        for version in versions:
            if version in ["common", latest]:
                self.parse_version(version, versions[version])

env = environment.Environment(env={})
p = Parser(env=env)
p.parse(t)
#p.env.list(sys.stdout)
#print p.env._sort_dependencies()
baked_env = p.env.flatten()
print baked_env.list(sys.stdout)


#print p.env.data





