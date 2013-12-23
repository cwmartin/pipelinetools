import os
import wafdefs
import subprocess
from waflib import Utils

class Waf3rdPartyPyModuleBuild(wafdefs.WafBuild):
    """
    """
    
    @classmethod
    def _set_install_prefix(cls, ctx):
        """
        """
        if ctx.options.publish:
            ctx.env.INSTALL_ROOT = os.path.dirname(wafdefs.MARCH_PYTHON_LIB_DIR)
        else:
            ctx.env.INSTALL_ROOT = os.path.dirname(wafdefs.MARCH_DEV_PYTHON_LIB_DIR)
        
        ctx.env.INSTALL_LIB = "lib"
                
    @classmethod
    def _configure(cls, cfg):
        """
        """
        if cfg.env.IS_WINDOWS:        
            cfg.env["MSVC_VERSIONS"] = ["wsdk 7.0"]
            cfg.env["MSVC_TARGETS"] = ["x64"]
            cfg.env["MSVC_COMPILER"] = "wsdk"        
            cfg.load(["msvc", "python"])
        else:
            cfg.load(["python", "gcc"])
        
    @classmethod
    def _get_wdsk_env(cls):
        """
        """        
        set_env = r'C:\Windows\System32\cmd.exe /E:ON /V:ON /T:0E /C "C:\Program Files\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.cmd"'
        popen = subprocess.Popen('%s %s & set' % (set_env, "/x64"),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        if popen.wait() != 0:
            raise Exception("SetEnv.cmd Failed")
        
        wdsk_env = {}
        for line in stdout.split("\n"):            
            if "=" not in line:
                continue
            line = line.strip()
            key, value = line.split("=", 1)
            wdsk_env[key] = value
        return wdsk_env
                    
    @classmethod
    def _build(cls, bld, modulename, version):
        """
        """        
        """
        python setup.py install --single-version-externally-managed 
        --install-lib="lib" --root="Q:\devel\cmartin\march\lib\python"
        """
        
        cls._set_install_prefix(bld)
        
        setup_py_file = os.path.join(bld.path.abspath(), "setup.py")
        python_exec = bld.env.PYTHON[0]
        
        bld.env.BUILD_DIR = bld.out_dir
        bld.env.MODULE_NAME = modulename
        bld.env.MODULE_VERSION = version
        
        #bld.env["DISTUTILS_USE_SDK"] = 1
        #bld.env["MSSdk"] = 1
        
        os.environ["DISTUTILS_USE_SDK"] = "1"
        os.environ["MSSdk"] = "1"
                
        def setup_py_install(task):
            """
            """
            #cmd = "%s %s install --single-version-externally-managed "\
            #    "--install-lib %s --root=%s" % (python_exec, setup_py_file,
            #                        bld.env.INSTALL_LIB, bld.env.INSTALL_ROOT)
            
            cmd = Utils.subst_vars('${PYTHON} setup.py install --single-version-externally-managed '\
                             '--install-lib="lib" --root="${BUILD_DIR}/3rdParty/python"', bld.env)
            
            task.exec_command(cmd, cwd=bld.path.abspath())
            
        def setup_py_build(task):
            """
            """
            if bld.env.IS_WINDOWS:
                wsdk_env = cls._get_wdsk_env()
                cmd = Utils.subst_vars('${PYTHON} setup.py build'\
                    ' --build-base="${BUILD_DIR}/3rdParty/python/${MODULE_NAME}_${MODULE_VERSION}"'\
                    ' --build-platlib="${BUILD_DIR}/3rdParty/python/${MODULE_NAME}_${MODULE_VERSION}/${PLATFORM_NAME}"'\
                    ' --compiler=msvc', bld.env)
                task.exec_command(cmd, cwd=bld.path.abspath(), env=wsdk_env)
            else:
                cmd = Utils.subst_vars('${PYTHON} setup.py build'\
                    ' --build-base="${BUILD_DIR}/3rdParty/python/${MODULE_NAME}_${MODULE_VERSION}"'\
                    ' --build-platlib="${BUILD_DIR}/3rdParty/python/${MODULE_NAME}_${MODULE_VERSION}/${PLATFORM_NAME}"',
                    bld.env)
                task.exec_command(cmd, cwd=bld.path.abspath(), env=wsdk_env)
                
                                        
        if bld.is_install > 0:            
            bld(rule=setup_py_install)
        
        if bld.cmd == "clean":
            build_dir = bld.path.make_node("build")            
            if os.path.exists(build_dir.abspath()):
                for n in build_dir.ant_glob("**/*"):
                    n.delete()
                build_dir.delete()
                
        bld(rule=setup_py_build)
            
            
             
            
                    
            
        
        
        
        