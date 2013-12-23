"""
Base Waf Build Definitions.
"""

import os
import platform
from waflib import Context

"""
WAF
"""

class WafBuild(object):

    @classmethod
    def top(cls):
        """
        """
        return os.path.join(os.environ.get("TBE_SRC_ROOT"))

    @classmethod
    def out(cls):
        """
        """
        return os.path.join(os.environ.get("TBE_SRC_ROOT"), "build")

    @classmethod
    def recurse(cls, ctx, func_name, subdirs=None):
        """
        Recurse subdirectories and perform the Waf func specified by the
        func_name.
        @param ctx Waf Context.
        @param func_name The Waf function to perform. eg: "build"
        @param subdirs A list of relative sub directores to traverse. If None,
        all subdirectories are traversed.
        """
        if subdirs is None:
            subdirs = ctx.path.ant_glob("*", dir=True, src=False)
            subdirs = [ n.path_from(n.parent) for n in subdirs ]
        ctx.recurse(subdirs, func_name, mandatory=True)

    @classmethod
    def configure(cls, cfg):
        """
        Default Waf configure.
        """

        cfg.env.OPTION_GROUP = "ToonBox Options"
        cfg.env.PLATFORM = platform.system()

        if cfg.env.PLATFORM == "Windows":
            cfg.env.PLATFORM_NAME = "windows"
            cfg.env.COPY = "copy"
        elif cfg.env.PLATFORM == "Linux":
            cfg.env.PLATFORM_NAME = "linux"
            cfg.env.COPYC = "cp"
        elif cfg.env.PLATFORM == "Darwin":
            cfg.env.PLATFORM_NAME = "osx"
            cfg.env.COPY = "cp"

        if cfg.options.publish:
            cfg.env.INSTALL_CHMOD = 505
        else:
            cfg.env.INSTALL_CHMOD = 777

        Context.run_dir = cfg.path.abspath()


        if cfg.options.tools_root is None:
            cfg.env.PREFIX = os.environ.get("TBE_TOOLS_ROOT")
        else:
            cfg.enb.PREFIX = cfg.options.tools_root

        cls._configure(cfg)

    @classmethod
    def _configure(cls, cfg):
        """
        Subclasses should implement this method to define their own configures.
        It is run after the default configure.
        """
        pass

    @classmethod
    def options(cls, opt):
        """
        Default Waf options.
        """
        opt_group = opt.add_option_group("ToonBox Options")
        opt_group.add_option('--publish', dest='publish', default=False, action='store_true', help='Publish to production')
        opt_group.add_option('--stage', dest='publish', default=False, action='store_true', help='Publish to production')
        opt_group.add_option('--tools_root', dest='tools_root', default=None, action='store')

        cls._options(opt)

    @classmethod
    def tbe_option_group(cls, opt):
        """
        Return the March Waf options group to add command line options to.
        """
        return opt.get_option_group(opt.env.OPTION_GROUP)

    @classmethod
    def _options(cls, opt):
        """
        Subclasses should implement this method to define their own options. It
        is run after the default options.
        """
        pass

    @classmethod
    def build(cls, bld, *args, **kwargs):
        """
        The default Waf build.
        """

        recurse = kwargs.pop("recurse", False)
        subdirs = kwargs.pop("subdirs", None)


        cls._build(bld, *args, **kwargs)
        if recurse:
            cls.recurse(bld, "build", subdirs=subdirs)

    @classmethod
    def _build(cls, bld, *args, **kwargs):
        """
        Subclasses should implement this method to define their own build.
        It is run after the defaulft build.
        """
        pass