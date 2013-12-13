"""
Waf Python Module Build
"""
import os
import wafdefs
from waflib import Utils

class WafPythonModuleBuild(wafdefs.WafBuild):
    """
    """
    
    @classmethod
    def _set_install_prefix(cls, ctx):
        """
        """
        if ctx.options.publish:
            ctx.env.INSTALL_PYTHON_PATH = ctx.env.TBX_PYTHON_PATH
        else:
            ctx.env.INSTALL_PYTHON_PATH = ctx.env.TBX_DEV_PYTHON_PATH
        
    @classmethod
    def _build(cls, bld, module_path, module_version, pyfiles=None, exclude_files=None):
        """
        @param module_path The dot (.) seperated full module path to install to.
        @param module_version Module version number.
        @param pyfiles A list of python files to build. If None then "*.py" is used.
        @param exclude_files A list for files to exclude from the build.
        """
        exclude_files = exclude_files or []
        if pyfiles is None:                     
            pyfiles = bld.path.ant_glob("*.py") 
        if isinstance(pyfiles, basestring):
            pyfiles = bld.path.ant_glob(pyfiles)
            
        module_path = module_path.replace(".", os.path.sep)
        unversioned_module_path = os.path.join("${INSTALL_PYTHON_PATH}", module_path)
        versioned_module_path = os.path.join("${INSTALL_PYTHON_PATH}", "%s_%s" % (module_path, module_version))

        cls._set_install_prefix(bld)

        for pyfile in pyfiles:
            
            pyfile_str = str(pyfile)
            
            if pyfile_str in exclude_files:
                continue
            
            build_target = "%s.out" % pyfile_str
            
            bld(source=pyfile_str, target=build_target, rule='${COPY} ${SRC} ${TGT}')
                        
            install_file = os.path.join(versioned_module_path, pyfile_str)

            bld.install_as(install_file, build_target)

        versioned_module_path = Utils.subst_vars(versioned_module_path, bld.env)                
        bld.symlink_as(unversioned_module_path, versioned_module_path)