import os
import yaml
import platform
import logging

log = logging.getLogger(__name__)

# DEFAULT_DIRMAP_FILE = "%s/src/config/dirmap.yml" % os.environ("TBE_TOOLS_ROOT")

DEFAULT_DIRMAP_FILE = r"C:\Users\Christopher\Google Drive\github\pipelinetools\python\lib\pipelinetools\dirmap.yml"

def read_dirmap():
    """
    """
    dirmap_file = os.environ.get("TBE_DIRMAP_FILE", False)
    if not dirmap_file:
        dirmap_file = DEFAULT_DIRMAP_FILE

    with open(dirmap_file, "r") as dirmap_file:
        dirmaps_data = yaml.load(dirmap_file.read())

    dirmaps = dirmaps_data["dirmaps"]
    return dirmaps

def dirmap(path, os_name=None):
    """

    """
    log.debug("Dirmapping path: '%s'" % path)

    curr_platform = platform.system().lower()

    if (os_name is None or os_name == curr_platform ) and os.path.exists(path):
        log.debug("Path found, skipping dirmap")
        return path

    if os_name is None:
        os_name = curr_platform

    dirmaps = read_dirmap()

    for dirmap in dirmaps:
        for dirmap_platform in dirmap:
            if path.startswith(dirmap[dirmap_platform]):
                repl = dirmap[os_name]
                return path.replace(dirmap[dirmap_platform], repl)
    raise Exception("Unable to find dirmap for path '%s'" % path)

print dirmap("/mnt/T/mypath/blarg")