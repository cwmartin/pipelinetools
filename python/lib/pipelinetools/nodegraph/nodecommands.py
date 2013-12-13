import commands
import constants
import nodeparam




class AddParamCommand(commands.Command):
    """
    """
    _COMMAND_NAME = "addparam"
    
    def _execute(self, node, name, param_type, param_mode, default_value=constants.NULL_VALUE):
        """
        """
        param_name = _get_unique_param_name(node, name, param_mode)
        param = NodeParam(node, param_name, param_type, param_mode,
                      default_value=default_value, user_param=True)
        self._input_params[param_name] = param
        return param

    def _undo(self):
        """
        """

class RemoveParamCommand(commands.Command):
    """
    """
    _COMMAND_NAME = "removeparam"

    pass

class RenameParamCommand(commands.Command):
    """
    """
    _COMMAND_NAME = "renameparam"

    pass

class SetValueCommand(commands.Command):
    """
    """
    _COMMAND_NAME = "setvalue"
    pass