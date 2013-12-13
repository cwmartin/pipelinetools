import weakref
import registry

class CommandError(Exception):
    """    
    """
    def __init__(self, command, msg):
        """
        """
        msg = "Error running command '%s'. %s" % (command, msg)
        Exception.__init__(self, msg.strip())

class CommandWarning(Exception):
    def __init__(self, command, msg):
        """
        """
        msg = "Warning running command '%s'. %s" % (command, msg)
        Exception.__init__(self, msg.strip())

class CommandExecuteError(Exception):
    """
    """
    pass

class CommandExecuteWarning(Excpetion):
    """
    """
    pass

class CommandUndoError(Exception):
    """
    """
    def __init__(self, command, msg):
        """
        """
        msg = "Unable to undo command '%s'. %s" % (command, msg)
        Exception.__init__(self, msg.strip())

class CommandRegistry(registry.Registry):
    """
    """
    pass

class CommandStack(object):
    """
    """
    def __init__(self, session):
        """
        """
        self._session = session
        self._stack = []

    def call(self, command, *args, **kwargs):
        """
        """
        command_cls = CommandRegistry.get(command)
        if command_cls is None:
            raise CommandError(command, "Command does not exist.")
        command_inst = command_cls(self._session)
        try:
            command_return = command_inst.execute(command_inst.execute(*args, **kwargs))
        except CommandExecuteWarning, why:
            raise CommandWarning(command_inst, why)
        except CommandExecuteError, why:
            raise CommandError(command_inst, why)
        except Exception, why:
            raise CommandError(command_inst, why)

        self._stack.append(command_inst)

    def undo(self):
        """
        """
        if self._stack:
            command_inst = self._stack.pop()
            try:
                command_inst.undo()
            except Exception, why:
                raise CommandUndoError(command_inst, why)
    
class _CommandMeta(type):
    """
    """
    def __init__(cls, name, bases, clsdict):
        """
        """
        super(_CommandMeta, cls).__init__(name, bases, clsdict)        
        if cls._COMMAND_NAME:
            CommandRegistry.register(cls._COMMAND_NAME, cls)        

class Command(object):
    """
    """

    __metaclass__ = _CommandMeta

    _COMMAND_NAME = ""

    def __init__(self, modifier=None, parent=None):
        """
        """
        self.modifier = modifier
        self._children = []
        if parent:
            self.parent._children.append(self)        

    def execute(self, *args, **kwargs):
        """
        """
        self._execute(*args, **kwargs)

    def _execute(self, *args, **kwargs):
        """
        """
        pass

    def undo(self):
        """
        """
        if self._children:
            while True:
                try:
                    child = self._children.pop()
                except:
                    break
                child.undo()
        self._undo()

    def _undo(self):
        """
        """
        pass

    def __str__(self):
        """
        """
        return self._COMMAND_NAME

    def __repr__(self):
        """
        """
        return self.__str__()

class 