

class RealmParser(object):
    """
    """
    def __init__(self):
        pass

    def parse(self, realm_data):
        """
        """
        realm_data = realm_data.get("realm")
        components_data = realm_data.get("components", None)
        self._parse_components(components_data)

    def _parse_components(self, components_data):
        """
        """
        for component_name, component_ident in components_data.items():
            print component_name, component_ident

if __name__ == "__main__":
    parser = RealmParser()

    realm_data = {"realm":{"components":{"maya":"default", "prman":"default", "katana":"default"}}}

    parser.parse(realm_data)

