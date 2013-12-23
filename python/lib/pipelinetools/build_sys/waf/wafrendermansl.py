"""
Waf Maya MEL Script Build
"""
import os
import wafdefs

SHADER_CMD = "shader"

class WafRendermanSLBuild(wafdefs.WafBuild):
    """
    """
    @classmethod
    def _set_install_prefix(cls, ctx):
        """
        """
        ctx.env.SHADER_PATH = os.path.join(ctx.env.PREFIX, "lib", "shaders")


    @classmethod
    def _build(cls, bld, sl_files=None, exclude_files=None):
        """
        @param exclude_files A list for files to exclude from the build.
        """
        exclude_files = exclude_files or []
        if sl_files is None:
            sl_files = bld.path.ant_glob("*.sl")
        if isinstance(sl_files, basestring):
            sl_files = bld.path.ant_glob(sl_files)

        cls._set_install_prefix(bld)

        for sl_file in sl_files:
            sl_file_str = str(sl_file)

            if sl_file_str in exclude_files:
                continue
            
            slo = "%s.slo" % os.path.splitext(os.path.basename(sl_file_str))[0]
            build_target = "%s.slo" % os.path.splitext(sl_file_str)[0]

            bld(source=sl_file_str, target=build_target, rule="shader -o ${TGT} ${SRC}")
            #bld(source=sl_file_str, target=build_target, rule='cp ${SRC} ${TGT}')

            install_file = os.path.join("${SHADER_PATH}", slo)
            bld.install_as(install_file, build_target)