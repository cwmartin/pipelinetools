"""
Waf Python Application Build
"""

import os
import wafdefs

HASHBANG_WINDOWS = "@echo off & python -x %0 %* &goto :eof"
HASHBANG_LINUX = "#!/opt/python"
HASHBANG_OSX = "#!/opt/python"

class WafPythonAppBuild(wafdefs.WafBuild):
    """
    """
                
    @classmethod
    def _set_install_prefix(cls, ctx):
        """
        Set the install prefix to use based on whether or not it's a prod publish
        """
        if ctx.options.publish:
            ctx.env.INSTALL_BIN_ROOT_PATH = ctx.env.MARCH_BIN_ROOT_PATH
        else:
            ctx.env.INSTALL_BIN_ROOT_PATH = ctx.env.MARCH_DEV_BIN_ROOT_PATH
    
    @classmethod
    def hashbang_insert(cls, task):
        """
        Waf Task for inserting hashbang at top of python app files.
        """    
        src = task.inputs[0]    
        tgt = task.outputs[0]
            
        hashbang = task.generator.hashbang
        source_data = src.read(flags="r")
        source_data = "%s\n%s" % (hashbang, source_data)
        source_data = source_data.replace('\r\n', '\n').replace('\r', '\n')
        tgt.write(source_data)
    
    @classmethod
    def _build(cls, bld, appname, pyfile=None):
        """
        Build the python app. Installing into devel and prod contexts.
        @param appname The name for the python app.
        @param py_file The python application file.  
        """    
        if pyfile is None:                     
            pyfile = bld.path.ant_glob("%s.py" % appname)[0]
        else:         
            pyfile = bld.path.ant_glob(pyfile)[0]
                                           
        cls._set_install_prefix(bld)
                    
        pyfile_str = str(pyfile)
            
        opsys_builds = {bld.env.BIN_SUB_WINDOWS: ["%s.%s" % (appname, bld.env.BIN_SUB_WINDOWS), 
                                   "%s.bat" % appname, HASHBANG_WINDOWS],
                        bld.env.BIN_SUB_LINUX: ["%s.%s" % (appname, bld.env.BIN_SUB_LINUX), 
                                 appname, HASHBANG_LINUX],
                        bld.env.BIN_SUB_OSX: ["%s.%s" % (appname, bld.env.BIN_SUB_OSX), 
                                 appname, HASHBANG_OSX]}
        
        for opsys in opsys_builds:
            build_target, appname, hashbang = opsys_builds[opsys]            
            
            #BUILD
            bld(source=pyfile_str, target=build_target, hashbang=hashbang, 
                rule=cls.hashbang_insert)
            
            #INSTALL
            install_file = os.path.join("${INSTALL_BIN_ROOT_PATH}", opsys, appname)        
            bld.install_as(install_file, build_target)
