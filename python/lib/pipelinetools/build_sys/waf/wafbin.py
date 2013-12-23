"""
Waf Bin Script Build
"""
import os
import wafdefs

class WafBinScriptBuild(wafdefs.WafBuild):
    """
    """
    @classmethod
    def _set_install_prefix(cls, ctx):
        """
        """
        ctx.env.BIN_PATH = os.path.join(ctx.env.PREFIX, "bin")

    @classmethod
    def _build(cls, bld, bin_files=None, exclude_files=None):
        """
        @param bin_files A list of scripts files to build. If None then "*.*" is used.
        @param exclude_files A list for files to exclude from the build.
        """

        cls._set_install_prefix(bld)
        bld.install_files("${BIN_PATH}", bld.path.ant_glob('*.*', excl=["wscript"]), cwd=bld.path)
        bld.install_files("${BIN_PATH}", bld.path.ant_glob('**/*', excl=["wscript"]), cwd=bld.path, relative_trick=True)