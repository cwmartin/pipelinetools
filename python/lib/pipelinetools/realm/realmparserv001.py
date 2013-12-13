"""
"""
import platform
import re
import sys
import yaml
from pipelinetools.utils import environment

class RealmEnvParserError(Exception):pass


class RealmConfigReader(object):
    """
    """
    def _read(self, realm_data):
        """
        """
        parser = RealmEnvParser()
        parser.parse(realm_data)
        env = parser.get_environment()

class JSONRealmReader(object):
    """
    """
    def _remove_comments(self, json_str):
        """
        """
        json_str = re.sub(re.compile("/\*.*?\*/", re.DOTALL), "", json_str)
        json_str = re.sub(re.compile("//.*?\n"), "", json_str)
        return json_str

    def read(self, realm_file):
        """
        """
        json_f = open(realm_file, "r")
        json_str = self._remove_comments(json_f.read())

        realm_data = json.loads(json_str)

        parser = RealmItemParser()
        parser.parse(realm_data)
        env = parser.get_environment()

        return env.flatten()

import yaml.constructor
from pipelinetools.utils.ordereddict import OrderedDict
class OrderedDictYAMLLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

class YAMLRealmReader(object):
    """
    """
    def read(self, realm_file):
        """
        """
        yaml_f = open(realm_file, "r")
        yaml_str = yaml_f.read()

        realm_data = yaml.load(yaml_str, OrderedDictYAMLLoader)
        parser = RealmItemParser()
        parser.parse(realm_data)
        env = parser.get_environment()

        return env.flatten()

class RealmItem(object):
    """
    """
    def __init__(self):
        """
        """
        self.aliases = {}
        self.environments = {}
        self.requires = {}

    def variants(self):
        """
        """
        return self.environments.keys()

    def get_environment(self, key=None):
        """
        """


class RealmItemParser(object):
    """
    """
    def __init__(self):
        """
        """
        self._common_env = environment.Environment(env={})
        self._variant_envs = {}
        self._curr_env = None
        self._platform = platform.system().lower()

    def parse(self, config, platform=None):
        """
        """
        if platform is not None:
            self._platform = platform
        self._parse_config(config)

    def get_environment(self, variant=None):
        """
        """
        if variant is None:
            variant = self.variant_variant

        if variant not in self._variant_envs:
            raise RealmEnvParserError("No environment for variant '%s'" % variant)
        return self._variant_envs[variant]


    def _parse_config(self, config):
        """
        """
        self.variant_variant = config.get("default")

        self._curr_env = self._common_env

        root_realmdef_block = config.get("realm-def", None)
        if root_realmdef_block:
            self._parse_realmdef_block(root_realmdef_block)

        variants_block = config.get("variants", None)
        if variants_block:
            self._parse_variants_block(variants_block)

    def _parse_realmdef_block(self, realmdef_block):
        """
        """
        environment_block = config.get("environment", None)
        if environment_block:
            self._parse_environment_block(environment_block)
        aliases_block = config.get("aliases", None)
        if aliases_block:
            self._parse_aliases_block(aliases_block)


    def _parse_environment_block(self, environment_block):
        """
        """
        common_env_block = environment_block.get("common", None)
        if common_env_block:
            self._parse_enviornment_vars_block(common_env_block)
        platform_env_block = environment_block.get(self._platform, None)
        if platform_env_block:
            self._parse_enviornment_vars_block(platform_env_block)

    def _parse_enviornment_vars_block(self, environment_vars_block):
        """
        """
        for env_key, env_val in environment_vars_block.items():
            self._curr_env.set(env_key, env_val)

    def _parse_variants_block(self, variants_block):
        """
        """
        for variant_key, variant_block in variants_block.items():
            self._curr_env = environment.Environment(env=self._common_env)
            self._parse_variant_block(variant_block)
            self._variant_envs[str(variant_key)] = self._curr_env

    def _parse_variant_block(self, variant_block):
        """
        """
        #TODO: parse requires block
        environment_block = variant_block.get("environment", None)
        if environment_block:
            self._parse_environment_block(environment_block)

    def _parse_aliases_block(self, aliases_block):
        """
        """
        pass

if __name__ == "__main__":

    # reader = JSONRealmReader()
    # env = reader.read("testconfig.json")
    # env.list(sys.stdout)

    reader = YAMLRealmReader()
    env = reader.read("testconfig.yaml")
    flattened_env = env.flatten(var_sub_platform="linux")
    flattened_env.list(sys.stdout)
