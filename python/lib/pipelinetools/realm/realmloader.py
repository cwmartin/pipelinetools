import os
import realmparser

REALM_COMPONENT_PATH = "/home/christopher/gdrive/github/pipelinetools/python/lib/pipelinetools/realm"



class RealmComponentLoader(object):
    """
    """
    def _get_components(self):
        """
        """
        realm_component_files = {}
        component_path_files = os.listdir(REALM_COMPONENT_PATH)
        for component_path_file in component_path_files:
            full_path = os.path.join(REALM_COMPONENT_PATH, component_path_file)
            if os.path.isdir(full_path):
                continue
            if not component_path_file.startswith("realm_"):
                continue
            name, ext = os.path.splitext(component_path_file)
            component_name = name.split("realm_")[-1]

            realm_component_files[component_name] = full_path

        return realm_component_files

    def _read_component_file(self, component_file):
        """
        """
        realm_reader = realmparser.YAMLRealmComponentReader()
        realm_data = realm_reader.read(component_file)
        return realm_data


    def _gather_components(self, components):
        """
        """
        for component_name, component_file in components.items():
            self._read_component_file(component_file)

        """
        IF component in components
            IF passes version test
        """

component_loader = RealmComponentLoader()
components = component_loader._get_components()
component_data = {}
for component in components:
    component_file = components[component]
    component_data[component] = component_loader._read_component_file(component_file)
















