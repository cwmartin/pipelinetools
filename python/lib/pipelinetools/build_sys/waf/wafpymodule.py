"""
Waf Python Module Build
"""
import os
import wafdefs

class WafPythonPackageBuild(wafdefs.WafBuild):
    @classmethod
    def _set_install_prefix(cls, ctx):
        """
        """
        ctx.env.LIB_PYTHON_PATH = os.path.join(ctx.env.PREFIX, "lib", "python")

    @classmethod
    def _build(cls, bld, package_name):
        """
        @param module_path The dot (.) seperated full module path to install to.
        @param pyfiles A list of python files to build. If None then "*.py" is used.
        @param exclude_files A list for files to exclude from the build.
        """

        cls._set_install_prefix(bld)

        bld.install_files("/".join(("${LIB_PYTHON_PATH}", package_name)), bld.path.ant_glob('*.py'), cwd=bld.path)
        bld.install_files("/".join(("${LIB_PYTHON_PATH}", package_name)), bld.path.ant_glob('**/*.py'), cwd=bld.path, relative_trick=True)

class WafPythonModuleBuild(wafdefs.WafBuild):
    """
    """
    @classmethod
    def _set_install_prefix(cls, ctx):
        """
        """
        ctx.env.LIB_PYTHON_PATH = os.path.join(ctx.env.PREFIX, "lib", "python")

    @classmethod
    def _build(cls, bld, module_path, pyfiles=None, exclude_files=None):
        """
        @param module_path The dot (.) seperated full module path to install to.
        @param pyfiles A list of python files to build. If None then "*.py" is used.
        @param exclude_files A list for files to exclude from the build.
        """
        exclude_files = exclude_files or []

        cls._set_install_prefix(bld)

        if pyfiles is None:
            pyfiles = bld.path.ant_glob("*.py")

        if isinstance(pyfiles, basestring):
            pyfiles = bld.path.ant_glob(pyfiles)

        module_path = module_path.replace(".", os.path.sep)

        cls._set_install_prefix(bld)

        for pyfile in pyfiles:
            pyfile_str = str(pyfile)

            if pyfile_str in exclude_files:
                continue

            build_target = "%s.out" % pyfile_str

            bld(source=pyfile_str, target=build_target, rule='cp ${SRC} ${TGT}')

            install_file = os.path.join("${LIB_PYTHON_PATH}", module_path, pyfile_str)

            bld.install_as(install_file, build_target)