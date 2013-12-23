"""
Waf Maya MEL Script Build
"""
import os
import wafdefs

class WafMELScriptBuild(wafdefs.WafBuild):
    """
    """


    @classmethod
    def _set_install_prefix(cls, ctx):
        """
        """
        ctx.env.LIB_MEL_PATH = os.path.join(os.environ.get("TOOLS_ROOT"), "lib", "mel")

    @classmethod
    def _build(cls, bld, mel_files=None, exclude_files=None):
        """
        @param module_path The dot (.) seperated full module path to install to.
        @param pyfiles A list of python files to build. If None then "*.py" is used.
        @param exclude_files A list for files to exclude from the build.
        """
        exclude_files = exclude_files or []
        if mel_files is None:
            mel_files = bld.path.ant_glob("*.mel")
        if isinstance(mel_files, basestring):
            mel_files = bld.path.ant_glob(mel_files)

        module_path = module_path.replace(".", os.path.sep)

        cls._set_install_prefix(bld)

        for mel_file in mel_files:
            mel_file_str = str(mel_file)

            if mel_file_str in exclude_files:
                continue

            build_target = "%s.out" % mel_file_str

            bld(source=mel_file_str, target=build_target, rule='cp ${SRC} ${TGT}')

            install_file = os.path.join("${LIB_PYTHON_PATH}", module_path, mel_file_str)
            bld.install_as(install_file, build_target)