import commands
import constants
import nodeparam

def _get_unique_node_name(node, param_name, param_mode):
    """
    Return a param name which is unique for the node based upon the given param_name. 
    If param_name already exists on the node for the given mode, an number is appended 
    to the name to make it unique.
    @param node Node to get a unique param name for.
    @param param_name Param name to test uniqueness of.
    @param param_mode Param mode i.e. INPUT or OUTPUT
    @returns str
    """
    _name = name
    inc = 1
    
    if mode == constants.INPUT:
        existing_params = node._input_params.keys()
    else:
        existing_params = node._output_params.keys()

    while _name in existing_params:
        _name = "%s%i" % (name, inc)
        inc += 1
    return _name


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