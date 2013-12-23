"""
"""
import os
import platform
from waflib import Context

class WafBuild(object):
    """
    """

    @classmethod
    def top(cls):
        """
        """
        return os.path.expandvars("$TBE_SRC_DIR")

    @classmethod
    def out(cls):
        """
        """
        return os.path.expandvars("$TBE_BUILD_DIR")

    @classmethod
    def recurse(cls, ctx, func_name, subdirs=None):
        """
        """
        if subdirs is None:
            subdirs = ctx.path.ant_glob("*", dir=True, src=False)
            subdirs = [ n.path_from(n.parent) for n in subdirs ]
        ctx.recurse(subdirs, func_name, mandatory=True)

    @classmethod
    def configure(cls, cfg):
        """
        """
        cfg.env.TBE_ROOT_PATH = os.path.expandvars("$TBE_ROOT_PATH")
        cfg.env.TBE_LIB_PATH = os.path.expandvars("$TBE_LIB_PATH")
        cfg.env.TBE_PYTHON_PATH = os.path.expandvars("$TBE_PYTHON_PATH")
        cfg.env.TBE_DOC_PATH = os.path.expandvars("$TBE_DOC_PATH")
        cfg.env.TBE_DEV_PYTHON_PATH = os.path.expandvars("$TBE_DEV_PYTHON_PATH")

        cfg.env.TBE_OPTION_GROUP = "ToonBox Options"
        cfg.env.PLATFORM = platform.system().lower()

        if cfg.env.PLATFORM == "windows":
            cfg.env.COPY = "copy"
        else:
            cfg.env.COPY = "cp"

        Context.run_dir = cfg.path.abspath()

        if cfg.options.publish:
            cfg.env.INSTALL_CHMOD = 505
        else:
            cfg.env.INSTALL_CHMOD = 777

        cls._configure(cfg)


    @classmethod
    def _configure(cls, cfg):
        """
        """
        pass

    @classmethod
    def options(cls, opt):
        """
        """                
        opt_group = opt.add_option_group("ToonBox Options")
        opt_group.add_option("--publish", default=False, action="store_true",        
            help="Publish to production.")

        opt_group.add_option("--stage", default=False, action="store_true",        
            help="Publish to staging.")

        cls._options(opt)

    @classmethod
    def _options(cls, opt):
        """
        """
        pass

    @classmethod
    def build(cls, bld, *args, **kwargs):
        """
        """
        recurse = kwargs.pop("recurse", False)
        subdirs = kwargs.pop("subdirs", None)

        cls._build(bld, *args, **kwargs)

        if recurse:
            cls.recurse(bld, "build", subdirs=subdirs)

    @classmethod
    def _build(cls, bld, *args, **kwargs):
        """
        """
        pass



