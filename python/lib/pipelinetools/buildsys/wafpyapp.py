"""
"""
import os
import wafdefs

HASHBANG_WINDOWS = "@echo off & python -x %0 %* &goto :eof"
HASHBANG_LIXUX = "#!/opt/python"
HASHBANG_OSX = "#!/opt/python"

class WafPythonAppBuild(wafdefs.WafBuild):
    """
    """
    @classmethod
    def _set_install_prefix(cls, ctx):
        """
        """
        if ctx.options.publish:
            ctx.env.INSTALL_BIN_ROOT_PATH = ctx.env.TBX_BIN_ROOT_PATH
        else:
            ctx.env.INSTALL_BIN_ROOT_PATH = ctx.env.TBX_DEV_BIN_ROOT_PATH

    @classmethod
    def insert_hashbang(cls, task):
        """
        """
        src = task.inputs[0]
        tgt = task.outputs[0]

        hashbang = task.generator.hashbang
        source_data = src.read(flags="r")
        source_data = "%s\n%s" % (hashbang, source_data)
        source_data = source_data.replace("\r\n", "\n").replace("\r", "\n")
        tgt.write(source_data)

    @classmethod
    def _build(cls, bld, appname, appversion, pyfile=None):
        """
        """
        if pyfile is None:
            pyfile = bld.path.ant_glob("%s.py" % appname)[0]
        else:
            pyfile = bld.path.ant_glob(pyfile)[0]

        cls._set_install_prefix(bld)

        pyfile_str = str(pyfile)


        opsys_builds = {[bld.env.TBX_BIN_WINDOWS:["%s.windows" % appname, "%s.bat" % appname, HASHBANG_WINDOWS],
                        [bld.env.TBX_BIN_LINUX:["%s.linux" % appname, appname, HASHBANG_LIXUX],
                        [bld.env.TBX_BIN_OSX:["%s.osx" % appname, appname, HASHBANG_OSX]}

        for opsys_bin in opsys_builds:
            build_target, appname, hashbang = opsys_build[opsys_bin]

            bld(source=pyfile_str, target=build_target, hashbang=hashbang,
                rule=cls.insert_hashbang)

            install_files = os.path.join("${INSTALL_BIN_ROOT_PATH}", opsys_bin, appname)
            bld.install_as(install_file, build_target)

