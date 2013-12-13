import re

class RealmRequiresVersionCompare(object):
    """
    """
    @classmethod
    def cmp(cls, a, b):
        """
        """
        version_pattern = re.compile(r"[\.|v]?([0-9a-zA-Z]+)")

        a_versions = version_pattern.findall(a)
        b_versions = version_pattern.findall(b)

        for a, b in zip(a_versions, b_versions):
            cmp_val = cmp(a, b)
            if cmp_val != 0:
                return cmp_val
        return 0

class RealmRequiresEngine(object):pass

if __name__ == "__main__":
    print RealmRequiresVersionCompare.cmp("7.3v4r102", "7.3v4r103")