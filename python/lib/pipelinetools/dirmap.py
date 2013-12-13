"""

"""
import os
import yaml
import platform
import logging
import sys

log = logging.getLogger(__name__)

# DEFAULT_DIRMAP_FILE = "%s/src/config/dirmap.yml" % os.environ("TBE_TOOLS_ROOT")

class DirmapError(Exception):pass

DEFAULT_DIRMAP_FILE = r"C:\Users\Christopher\Google Drive\github\pipelinetools\python\lib\pipelinetools\dirmap.yml"

def _read_dirmap():
    """
    Load the dirmap from the dirmap file.
    """
    dirmap_file = os.environ.get("TBE_DIRMAP_FILE", False)
    
    if not dirmap_file:
        dirmap_file = DEFAULT_DIRMAP_FILE

    if not os.path.exists(dirmap_file):
        raise DirmapError("Unablet to find dirmap file: '%s'" % dirmap_file)
        
    with open(dirmap_file, "r") as dirmap_file:
        dirmaps_data = yaml.load(dirmap_file.read())

    dirmaps = dirmaps_data["dirmaps"]
    return dirmaps

def dirmap(path, os_name=None):
    """
    Find the mapping for a path. This will run through all directory mappings
    looking for a path match. If found, returns the remapped path.
    @param path The path to remap
    @param os_name If specified, remap the path to the specified OS. If None, the 
    current OS is used. Valid values are "linux" and "windows"
    @return Remapped path string.
    """
    log.debug("Dirmapping path: '%s'" % path)

    curr_platform = platform.system().lower()

    if (os_name is None or os_name == curr_platform ) and os.path.exists(path):
        log.debug("Path found, skipping dirmap")
        return path

    if os_name is None:
        os_name = curr_platform

    dirmaps = _read_dirmap()

    for dirmap in dirmaps:
        for dirmap_platform in dirmap:
            if path.startswith(dirmap[dirmap_platform]):
                repl = dirmap[os_name]
                return path.replace(dirmap[dirmap_platform], repl)

    raise DirmapError("Unable to find dirmap for path '%s'" % path)

if __name__ == "__main__":
    import optparse

    parser = optparse.OptionParser(usage="usage: dirmap [options] path")
    parser.add_option("-o", "--os", action="store", dest="os_name", default=None,
        help="OS to remap to. Valid values are 'linux' and 'windows'")

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.print_usage()
        sys.exit(-1)

    try:
        path = dirmap(args[0], os_name=options.os_name)
        print path
        sys.exit(0)
    except DirmapError, why:
        print why
        sys.exit(-2)