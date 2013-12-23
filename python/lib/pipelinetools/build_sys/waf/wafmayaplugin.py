"""
Waf Maya Plugin Build
"""
import os
import wafdefs
from wafmayascript import WafMayaScriptBuild

class WafMayaPluginBuild(wafdefs.WafBuild):
    """
    """
    
    MAYA_VERSIONS = ["2011", "2012"]    
    
    @classmethod
    def _set_install_prefix(cls, ctx):
        """
        """
        if ctx.options.publish:
            ctx.env.INSTALL_PYTHON_LIB_PATH = ctx.env.MARCH_PYTHON_LIB_DIR
        else:
            ctx.env.INSTALL_PYTHON_LIB_PATH = ctx.env.MARCH_DEV_PYTHON_LIB_DIR
    
    @classmethod
    def _set_maya_loc(cls, ctx, version):
        """
        """
        if ctx.env.IS_WINDOWS:
            maya_loc = "C:/Program Files/Autodesk/Maya%s" % version
        elif ctx.env.IS_LINUX:
            maya_loc = "/usr/autodesk/maya%s-x64" % version
        elif ctx.env.IS_OSX:
            maya_loc = None
        
        ctx.env.MAYA_LOC = maya_loc
            
    @classmethod
    def _options(cls, opt):
        """
        """
        opt_group = wafdefs.WafBuild.march_option_group(opt)
        opt_group.add_option('--maya_versions', dest='maya_versions', 
                             default="", action='store', help='Publish to production')
            
    @classmethod
    def _configure(cls, cfg):
        """        
        """                            
        if cfg.env.IS_WINDOWS:
            cfg.env.MAYA_LOC_PATTERN = "C:/Program Files/Autodesk/Maya%s"
            cls._msvc_setup(cfg)
        elif cfg.env.IS_LINUX:            
            cfg.env.MAYA_LOC_PATTERN = "/usr/autodesk/maya%s-x64"
            cls._gcc_linux_setup(cfg)
        elif cfg.env.IS_OSX:
            cls._gcc_osx_setup(cfg)
        else:
            cfg.fatal("Unhandled operating system: '%s'" % cfg.env.PLATFORM)
            
            
    @classmethod
    def _msvc_setup(cls, ctx):
        """
        """
        ctx.env["MSVC_VERSIONS"] = ["wsdk 7.0"]
        ctx.env["MSVC_TARGETS"] = ["x64"]
        ctx.env["MSVC_COMPILER"] = "wsdk"
        ctx.env["DSO_EXT"] = "mll"
        ctx.load("msvc")
                    
        ctx.env.append_value("DEFINES", ["NDEBUG", "WIN32", "_WINDOWS", "NT_PLUGIN",
                                         "REQUIRE_IOSTREAM", "Bits64_", "_WINDLL"])
        
        ctx.env.append_value('CXXFLAGS', ["/O2", "/Ob1", "/EHsc", "/MD"])
        ctx.env.append_value("LDFLAGS", ["/nologo", "/OPT:NOREF", "INCREMENTAL:NO"])
                                         
        ctx.env.append_value("LINKFLAGS", [
                                           "/MACHINE:X64", "/export:initializePlugin", 
                                           "/export:uninitializePlugin"])
        
        ctx.env.append_value("LIB", ["OpenMaya", "OpenMayaUI", "Foundation"])
        
    @classmethod
    def _gcc_linux_setup(cls, ctx):
        """
        """        
        ctx.env["CXX"] = "g++"            
        ctx.env["DSO_EXT"] = "so"
        ctx.load("g++")
        
        ctx.env.append_value("INCLUDES", ["/usr/X11R6/include", "/usr/include/"])
        
        ctx.env.append_value("DEFINES", ["NDEBUG", "LINUX", "LINUX_64", "_BOOL", 
                                         "REQUIRE_IOSTREAM"])
        
        ctx.env.append_value('CXXFLAGS', ["-m64", "-O3", "-pthread", "-pipe",
                                          "-fPIC", "-Wno-deprecated", 
                                          "-fno-gnu-keywords"])
        
        ctx.env.append_value("LINKFLAGS", ["-Wl", "-Bsymbolic", "-shared"])
        ctx.env.append_value("LIB", ["OpenMaya", "OpenMayaUI", "Foundation"])
                
    @classmethod
    def _gcc_osx_setup(cls, ctx):
        """
        """
        ctx.env["DSO_EXT"] = "bundle"
        
    @classmethod
    def _build(cls, bld, source, target, melfiles=None, includes=None, lib=None,
               libpath=None, defines=None, cxxflags=None, maya_versions=None):
        """
        @param source A list of the source files for the plugin.
        @param target The name of the .mll/.so plugin.
        @param melfiles A list of MEL files associated with the plugin
        that need to be built.
        @param includes A list of include paths to use.
        @param lib A list of libraries to use.
        @param libpath A list of library paths to use.
        @param defines A list of compiler defines to use.
        @param cxxflags A list of cxx flags to use.
        @param maya_versions A list of maya version to build for. eg: ["2011", "2011"]
        """
                                
        if bld.options.maya_versions:            
            bld.env.MAYA_VERSIONS = bld.options.maya_versions.split() 
        else:
            bld.env.MAYA_VERSIONS = cls.MAYA_VERSIONS
          
        for maya_verison in bld.env.MAYA_VERSIONS:
            if not os.path.exists(bld.env.MAYA_LOC_PATTERN % maya_verison):
                bld.fatal("Unable to locate Maya %s." % maya_verison)
        
        if includes:
            bld.env.append_unique("INCLUDES", includes)
        if lib:
            bld.env.append_unique("LIB", lib)
        if libpath:
            bld.env.append_unique("LIBPATH", libpath)
        if defines:
            bld.env.append_unique("DEFINES", defines)
        if cxxflags:
            bld.env.append_unique("CXXFLAGS", cxxflags)
                
        cls._set_install_prefix(bld)
        
        for maya_version in bld.env.MAYA_VERSIONS:
            
            maya_loc = bld.env.MAYA_LOC_PATTERN % maya_version
            bld.env.append_value("LIBPATH", ["%s/lib" % maya_loc])
            bld.env.append_value("INCLUDES", [".", "%s/include" % maya_loc])
            
            bld.objects(source=source, taret="dso_objects")            
            dso = bld.shlib(source=source, target=target, use="dso_objects")
                        
            dso.env.cxxshlib_PATTERN = "%s." + bld.env.DSO_EXT
            dso_target = dso.env.cxxshlib_PATTERN % target
                        
            install_file = os.path.join(bld.env.INSTALL_PYTHON_LIB_PATH, "maya", 
                                        "plug-ins", maya_version, dso_target)
            bld.install_as(install_file, dso_target, chmod=bld.env.INSTALL_CHMOD)
                        
        if melfiles:
            WafMayaScriptBuild._build(bld, melfiles)
        