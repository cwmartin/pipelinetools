import re
import sys
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.addHandler(logging.StreamHandler())

from shotgun_api3 import Shotgun

SERVER_PATH = "https://toonboxent.shotgunstudio.com"
SCRIPT_NAME = 'devel'     
SCRIPT_KEY = 'cc7c038a621d8e1a13217fa98a122843c89a09b4'

sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

project_re = r"\D{1}[^_]*"
sequence_re = r"[^_]*"
shot_re = r"\d+[^_]*"

EXPR_PATTERNS = [
#r"^(?P<prj>%s)$" % project_re,
r"^(?P<prj>%s)_q(?P<seq>%s)$" % (project_re, sequence_re),
r"^(?P<prj>%s)_q(?P<seq>%s)_s(?P<shot>%s)$" % (project_re, sequence_re, shot_re),
r"^q(?P<seq>%s)_s(?P<shot>%s)$" % (sequence_re, shot_re),
r"^q(?P<seq>%s)$" % sequence_re,
r"^s(?P<shot>%s)$" % shot_re]

EXPR_DELIMETER = ","
EXPR_RANGE_CHAR = "-"

class ShotExpressionState(object):
    """
    """
    def __init__(self):
        """
        """
        self.project = None
        self.sequence = None
        self.shot = None

        self.sequences = []

class ShotExpressionParser(object):
    """
    """
    def __init__(self, expr_patterns=None, expr_delimeter=None, expr_range_char=None):
        self.expr_patterns = expr_patterns or EXPR_PATTERNS
        self.expr_delimeter = expr_delimeter or EXPR_DELIMETER
        self.expr_range_char = expr_range_char or EXPR_RANGE_CHAR

        self._compile_expr_patterns()
        self._sequences = None
        self._shots = {}

    def _get_sequences(self, project, sequences=None):
        """
        """
        if self._sequences is None:
            self._sequences = {}
            sg_sequences = sg.find("Sequence", [("project.Project.sg_code", "is", project)], ["code"])
            for sg_sequence in sg_sequences:
                self._sequences[sg_sequence["code"]] = sg_sequence

        if sequences:
            ret_sequenecs = {}
            for sequence in sequences:
                ret_sequenecs[sequence] = self._sequences[sequence]
            return ret_sequenecs

        return self._sequences

    def _get_shots(self, project, sequences=None):
        """
        """
        sequences = self._get_sequences(project, sequences=sequences)
        
        fetch_sequences = []
        for sequence, sg_sequence in sequences.items():
            if not sequence.startswith("%s_" % project):
                sequence = "%s_%s" % (project, sequence)
            if sequence not in self._shots:
                fetch_sequences.append(sg_sequence)
        
        sg_shots = sg.find("Shot", [("project.Project.sg_code", "is", project), ("sg_sequence", "in", fetch_sequences)], ["code", "sg_sequence.Sequence.code"])

        for sg_shot in sg_shots:
            shot = sg_shot["code"]
            sequence = sg_shot["sg_sequence.Sequence.code"]

            if sequence not in self._shots:
                self._shots[sequence] = []
            self._shots[sequence].append(shot)

        return self._shots


    def _get_expr_shots(self, project, start_seq, end_seq=None, start_shot=None, end_shot=None):
        """
        """
        sequences = sorted(self._get_sequences(project).keys())

        #find the indices for the start and end sequences
        start_seq_index = sequences.index("%s_%s" % (project, start_seq))
        if end_seq:
            end_seq_index = sequences.index("%s_%s" % (project, end_seq))
        else:
            end_seq = start_seq
            end_seq_index = start_seq_index

        #swap the indexs if the end seq comes before the start seq
        if end_seq_index < start_seq_index: 
            _temp = start_seq_index
            start_seq_index = end_seq_index
            end_seq_index = _temp

        #get the range of sequences
        sequence_range = sequences[start_seq_index:end_seq_index+1]


        if start_shot:
            start_shot = "%s_%s_%s" % (project, start_seq, start_shot)
        if end_shot:
            end_shot = "%s_%s_%s" % (project, end_seq, end_shot)

        shots = self._get_shots(project, sequences=sequence_range)

        expanded_shots = []
        for seq_shots in shots.values():
            expanded_shots.extend(seq_shots)

        shots = sorted(expanded_shots)

        if start_shot is None and end_shot is None:
            return shots
        
        logger.debug("Start/End Shot: %s, %s" % (start_shot, end_shot))

        if start_shot:            
            start_shot_index = shots.index(start_shot)
        else:
            start_shot_index = 0

        if end_shot:
            end_shot_index = shots.index(end_shot)
        else:
            end_shot_index = None

        logger.debug("Start/End Index: %s, %s" % (start_shot_index, end_shot_index))

        if end_shot_index < start_shot_index:
            _temp = start_shot_index
            start_shot_index = end_shot_index
            end_shot_index = _temp

        return shots[start_shot_index:end_shot_index+1]

    def _compile_expr_patterns(self):
        """
        """
        _expr_patterns = []

        compiled_pattern_type = type(re.compile(""))

        for expr_pattern in self.expr_patterns:
            if isinstance(expr_pattern, compiled_pattern_type):
                continue
            _expr_patterns.append(re.compile(expr_pattern))
        self.expr_patterns = _expr_patterns

    def match_expr_pattern(self, expr, expr_state):
        """
        """
        expr_values = {"prj":expr_state.project, "seq":expr_state.sequence, "shot":None}

        for expr_pattern in self.expr_patterns:
            match = expr_pattern.match(expr)
            if match:
                expr_values.update(match.groupdict())
                expr_state.project = expr_values["prj"]
                expr_state.sequence = expr_values["seq"]
                expr_state.shot = expr_values["shot"]

                return expr_values
        return None

    def evaluate_expr_value(self, project, expr_value):
        """
        """
        sequences = self._get_sequences(project)
        if isinstance(expr_value, (list, tuple)):
            range_start_expr_value, range_end_expr_value = expr_value

            return self._get_expr_shots(range_start_expr_value["prj"], range_start_expr_value["seq"],
                end_seq=range_end_expr_value["seq"], start_shot=range_start_expr_value["shot"],
                end_shot=range_end_expr_value["shot"])

        else:
            return self._get_expr_shots(expr_value["prj"], expr_value["seq"], start_shot=expr_value["shot"])

        
    def parse_expr(self, expr):
        """
        """
        expr_state = ShotExpressionState()

        expr_elements = expr.split(self.expr_delimeter)

        shots = []

        for expr_element in expr_elements:
            if self.expr_range_char in expr_element:
                rh_expr_element, lh_expr_element = expr_element.split(self.expr_range_char)
                range_start_expr_values = self.match_expr_pattern(rh_expr_element, expr_state)
                range_end_expr_values = self.match_expr_pattern(lh_expr_element, expr_state)

                shots.extend(self.evaluate_expr_value(range_start_expr_values["prj"], (range_start_expr_values, range_end_expr_values)))
            else:
                expr_values = self.match_expr_pattern(expr_element, expr_state)
                if expr_values:
                    shots.extend(self.evaluate_expr_value(expr_values["prj"], expr_values))
    
        return sorted(list(set(shots)))

def parse_expr(expr):
    """
    """
    parser = ShotExpressionParser()
    return parser.parse_expr(expr)

if __name__ == "__main__":
    import optparse

    logger.setLevel(logging.INFO)

    usage = "usage: shexpr [options] arg"

    optparser = optparse.OptionParser(usage=usage)
    options, args = optparser.parse_args()

    if not args:
        optparser.print_usage()
        sys.exit(1)

    shots = parse_expr(args[0])
    print ", ".join(shots)
