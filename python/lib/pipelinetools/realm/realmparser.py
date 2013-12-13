"""
"""
import platform
import re
import sys
import yaml

import requiresengine

from pipelinetools.utils import yamlutils
from pipelinetools.utils import environment as env

class RealmEnvParserError(Exception):pass
class RealmComponentParserError(Exception):pass
class RealmDefError(Exception):pass

class RealmComponentReader(object):
    """
    Base Realm Config Data Reader
    """
    def read(self, realm_data):
        """
        @param realm_data A dict containing the realm data information
        """
        parser = RealmComponentParser()
        realm_defs, default_def = parser.parse(realm_data)
        return {"realm_defs":realm_defs, "default":default_def}

class JSONRealmComponentReader(RealmComponentReader):
    """
    JSON Realm Config Data Reader
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
        return RealmComponentReader.read(self, realm_data)

class YAMLRealmComponentReader(RealmComponentReader):
    """
    YAML Realm Config Data Reader
    """
    def read(self, realm_file):
        """
        """
        yaml_f = open(realm_file, "r")
        yaml_str = yaml_f.read()
        realm_data = yaml.load(yaml_str, yamlutils.OrderedDictYAMLLoader)
        return RealmComponentReader.read(self, realm_data)

class RealmComponentVaraint(object):
    """
    Container class for Realm component variant information.
    """
    def __init__(self, component_variant=None, environment=None, requires=None, aliases=None):
        """
        """
        if component_variant:
            self.environment = env.Environment(component_variant.environment)
            self.requires = component_variant.requires.copy()
            self.aliases = component_variant.aliases.copy()
        else:
            self.environment = environment or env.Environment(env={})
            self.requires = requires or {}
            self.aliases = aliases or {}

class RealmComponentParser(object):
    """
    """
    def __init__(self):
        """
        """

    def _get_component_parser(self, parser_cls=None):
        """
        """
        if parser_cls is None:
            return RealmComponentDefParser
        return parser_cls

    def _get_component_requires_engine(self, engine_cls=None):
        """
        """
        if engine_cls is None:
            return requiresengine.RealmRequiresEngine
        return engine_cls

    def parse(self, component_data, env_platform=None):
        """
        """
        component_parser_str = component_data.get("component-parser", None)
        component_parser_cls = self._get_component_parser(parser_cls=component_parser_str)
        component_parser = component_parser_cls()

        requires_engine_str = component_data.get("component-requires-engine", None)
        requires_engine_cls = self._get_component_requires_engine(engine_cls=requires_engine_str)
        requires_engine = requires_engine_cls()

        component_def = component_data.get("component-def", None)
        if component_def is None:
            raise RealmComponentParserError("Unable to find 'component-defs' declaration.")

        component_parser.parse(component_def, env_platform=env_platform)

        default = component_data.get("default")

        return component_parser.component_variants, default

class RealmComponentDefParser(object):
    """
    """
    def __init__(self):
        """
        """
        self._platform = platform.system().lower()
        self.component_variants = {}

    def parse(self, component_def, env_platform=None):
        """
        """
        if env_platform is not None:
            self._platform = env_platform
        self._parse_component_def(component_def)

    def _parse_component_def(self, component_def):
        """
        """
        #get the root definition
        root_variant = component_def.pop("root", None)

        #root def is required
        if root_variant is None:
            raise RealmComponentParserError("Unable to find 'root' for realm component definition.")

        root_variant = self._parse_variant_def(root_variant, root_variant=None)

        self.component_variants["root"] = root_variant

        for component_variant_name in component_def:
            component_variant = self._parse_variant_def(component_def[component_variant_name],
                                                    root_variant=root_variant)
            self.component_variants[component_variant_name] = component_variant

    def _parse_variant_def(self, variant_def, root_variant=None):
        """
        Parse a realm-def block from the realm config data.
        @param realm_def_block A dict containing a realm-def block.
        @param root_realm_def A RealmDef object containing the parsed root realm-def
        """
        component_variant = RealmComponentVaraint(component_variant=root_variant)

        environment_def = variant_def.get("environment", None)
        if environment_def:
            self._parse_environment_def(environment_def, component_variant.environment)

        requires_def = variant_def.get("requires", None)
        if requires_def:
            self._parse_requires_def(requires_def, component_variant.requires)

        aliases_def = variant_def.get("aliases", None)
        if aliases_def:
            self._parse_aliases_def(aliases_def, component_variant.aliases)

        return component_variant

    def _parse_environment_def(self, environment_def, environment):
        """
        """
        #parse the common, non-platform specific envs
        common_env_def = environment_def.get("common", None)
        if common_env_def:
            self._parse_enviornment_vars_def(common_env_def, environment)

        #parse the vars for the specified platform
        platform_env_def = environment_def.get(self._platform, None)
        if platform_env_def:
            self._parse_enviornment_vars_def(platform_env_def, environment)


    def _parse_enviornment_vars_def(self, environment_vars_def, environment):
        """
        """
        for env_key, env_val in environment_vars_def.items():
            environment.set(env_key, env_val)

    def _parse_aliases_def(self, aliases_def, aliases):
        """
        """
        common_aliases_def = aliases_def.get("common", None)
        if common_aliases_def:
            for key, value in common_aliases_def.items():
                aliases[key] = value
        platform_aliases_def = aliases_def.get(self._platform, None)
        if platform_aliases_def:
            for key, value in platform_aliases_def.items():
                aliases[key] = value

    def _parse_requires_def(self, requires_def, requires):
        """
        """
        common_requires_def = requires_def.get("common", None)
        if common_requires_def:
            for key, value in common_requires_def.items():
                requires[key] = value
        platform_requires_def = requires_def.get(self._platform, None)
        if platform_requires_def:
            for key, value in platform_requires_def.items():
                requires[key] = value

if __name__ == "__main__":
    reader = YAMLRealmComponentReader()
    realm_data = reader.read("realm_maya.yaml")
    realm_defs = realm_data["realm_defs"]
    realm_default = realm_data["default"]

    print realm_defs[realm_default].requires

