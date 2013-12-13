"""
Module for evaluating shot expressions.

The shot expression allows a user to query a list of shots from Tactic using ranges and short hand.
Below are some examples of how to use shot expressions.

Using an expression you can get a list of all shots in a range. For example:

'tnj_q002_s0010-s0040'

This expression will return all shots from q002_s0010 through q002_s0040. Note that since the
sequence has already been specified there is no need to specify it again in the right hand side of the
range expression.

You can select shots across multiple sequences by making sure to specify a sequence number on the
right hand side of the range. For exmaple:

'tnj_q002-q025'

The above expression will return all shots from every sequence between and including q002 and s025.

You can also use shot codes in an expression that crosses multiple sequences. For example:

'tnj_q002_s0100-q025_s0040'

This will return all shots from q002_s0100, all shots from every sequence between q002 and q025 and
finally, all shots from q025 up until s0040.

To get a list of all shots in a single sequence by simply using the sequence code. For example:

'tnj_q002'

To get a list of all shots in a project by using the project code. For example:

'tnj'

You can have multiple expression elements joined into a single expression by joining them with a
comma ','. For example:

'tnj_q002,tnj_q025,tnj_q100_s0010-s0100'

The above expression will return all shots from q002, all shots from q025 and all shots from q100_s0010
through q100_s0100.

**Note you must specify the project at least once at the begining of the expression i.e. If using
an expression for The Nut Job, the absolute basic expression string is 'tnj'. Also note that you
cannot cross projects in the expression.

A CSV file can also be used to define expressions. Expressions in a CSV file must be one expression
pre row and be in column 0.

For example, the string expression 'tnj_q002,tnj_q025,tnj_q100_s0010-s0100' could be expressed in a
CSV as:

'tnj_q002',
'tnj_q025',
'tnj_100_s0010-s0100'
"""

import re
import os
import csv

from shotgun_api3 import Shotgun

SERVER_PATH = "https://toonboxent.shotgunstudio.com"
SCRIPT_NAME = 'devel'     
SCRIPT_KEY = 'cc7c038a621d8e1a13217fa98a122843c89a09b4'

sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

SEQ_PADDING = 3
SHOT_PADDING = 4

project_re = r"\D{1}[^_]*"
sequence_re = r"[^_]*"
shot_re = r"\d+[^_]*"

EXPR_PATTERNS = [
r"^(?P<prj>%s)$" % project_re,
r"^(?P<prj>%s)_(?P<seq>%s)$" % (project_re, sequence_re),
r"^(?P<prj>%s)_(?P<seq>%s)_(?P<shot>%s)$" % (project_re, sequence_re, shot_re),
r"^(?P<seq>%s)_(?P<shot>%s)$" % (sequence_re, shot_re),
r"^(?P<seq>%s)$" % sequence_re,
r"^(?P<shot>%s)$" % shot_re]

EXPR_DELIMETER = ","
EXPR_RANGE_CHAR = "-"

class InvalidShotExprError(Exception):pass

class ShotExpressionParser(object):

    def __init__(self, project, expr_delimeter=None, expr_range_char=None, expr_patterns=None):
        """
        """
        self.project = project
        self.expr_delimeter = expr_delimeter or EXPR_DELIMETER
        self.expr_range_char = expr_range_char or EXPR_RANGE_CHAR
        self.expr_patterns = expr_patterns or EXPR_PATTERNS

        self._all_sequences = []

    def _get_sequences(self):
        """
        """
        if not self._all_sequences:
            self._all_sequences = [ x["code"] for x in sg.find("Sequence", [("project.Project.sg_code", "is", prj)], ["code"])]

        return self._all_sequences

    def _get_shots(self, seqs=None, shot=None):
        """
        Query for shots.
        @param seqs A list of sequence codes to return a list of shots from.
        @param shot A shot to query in Tactic.
        @returns a list of shot codes matching the seqs and/or shots.
        """

        filters = [("project.Project.sg_code", "is", self.project)]

        if shot:
            filters.append(("code", "is", shot))
        elif seqs:
            filters.append(("sg_sequence.Sequence.code", "in", seqs))

        columns = ["code"]

        shots = sg.find("Shot", filters, columns)

        if shots is None:
            return []

        return [ str(x["code"]) for x in shots ]


    def split_expr(self, expr):
        """
        Split an expression string into elements.
        @param expr An expression string to split.
        @returns a tuple containing all expression elements.
        """
        return ( x.strip() for x in expr.split(self.expr_delimeter))

    def split_range(expr):
        """
        Split an expression range element.
        @param expr An expression string to split.
        @returns A tuple containing the left hand and right hand arugments of a range expression element.
        """
        return ( x.strip() for x in expr.split(self.expr_range_char) )

    def _eval_expr_arg(self, expr_arg, seq=None):
        """
        Evaluate a single expression argument.
        @param expr_arg A single expression argument.
        @param prj Tactic project code.
        @param seq Current Tactic sequence code.
        @returns a argument value dict containing the prj, seq and shot
        """
        shot_values = {"prj":self.project, "seq":seq, "shot":None}

        #iterate over all expression patterns matching against the expression argument.
        for pattern in self.expr_patterns:
            m = re.match(pattern, expr_arg)
            #if a pattern match is found, get the argument values
            if m:
                shot_values.update(m.groupdict())
                return shot_values
        return None

    def _eval_expr_element(self, expr_element, seq=None):
        """
        Evaluate a single expression element.
        @param expr_element An expression element.
        @param prj Tactic project code.
        @param seq Current Tactic sequence code.
        @returns The current project, the current seq and a list of evaluated shots.
        """
        #if a shot range
        if self.expr_range_char in expr_element:
            start_shot = None
            end_shot = None

            lharg, rharg  = self.split_range(expr_element)

            range_start_vals = self._eval_expr_arg(lharg, seq=seq)

            if range_start_vals is None:
                raise InvalidShotExprError("Unable to evaluate expression argument '%s'" % lharg)

            range_end_vals = self._eval_expr_arg(rharg, seq=range_start_vals["seq"])

            if range_end_vals is None:
                raise InvalidShotExprError("Unable to evaluate expression argument '%s'" % rharg)

            seq = range_end_vals["seq"]

            try:
                range_shots = self._eval_shot_range(range_start_vals, range_end_vals)

            except Exception, why:
                raise InvalidShotExprError("Unable to evaluate shot range element '%s'. %s" %
                        (expr_element, why))

            return seq, range_shots

        else:

            arg_values = self._eval_expr_arg(expr_element, seq=seq)

            if arg_values is None:
                raise InvalidShotExprError("Unable to evaluate expression argument '%s'" % expr_element)

            seq = arg_values["seq"]
            shot = arg_values["shot"]

            print seq, shot

            shots = []

            if shot:
                shot = "%s_%s_%s" % (self.project, seq, shot)
                shots = self._get_shots(shot=shot)
            else:
                if seq:
                    shots = self._get_shots(seqs=["%s_%s" % (prj, seq)])
                else:
                    shots = self._get_shots()

            return seq, shots

    def _eval_shot_range(self, start_values, end_values):
        """
        @param start_values The range start values dict.
        @param end_values The range end values dict.
        @returns A list of evaluated shots.
        """

        start_seq = start_values["seq"]
        start_shot = start_values["shot"]

        end_seq = end_values["seq"] or start_seq
        end_shot = end_values["shot"]

        all_sequences = self._get_sequences()

        start_seq_index = all_sequences.find(start_seq)
        end_seq_index = all_sequences.find(end_seq)

        if start_seq_index == end_seq_index:
            seqs = [start_seq]

        else:
            if end_seq_index < start_seq_index:
                raise Exception("Range start sequence greater than range end sequence.")
            seqs = all_sequences[start_seq_index:end_seq_index]

        if len(seqs) > 1:
            shots = self._get_shots(seqs=seqs)



        codes = set()
        used_seqs = []

        #iterate over all sequence and shot numbers between the start and end range
        for seq_num in range(start_seq_num, end_seq_num + 1):
            seq = "%s_q%s" % (prj, str(seq_num).zfill(SEQ_PADDING))
            used_seqs.append(seq)

            if seq_num == start_seq_num:
                _start_shot_num = start_shot_num
            else:
                _start_shot_num = 0

            if seq_num == end_seq_num:
                _end_shot_num = end_shot_num
            else:
                _end_shot_num = int("9" * SHOT_PADDING)

            for shot_num in range(_start_shot_num, _end_shot_num + 1):
                shot_code = "%s_s%s" % (seq, str(shot_num).zfill(SHOT_PADDING))
                codes.add(shot_code)

        #get a list of all Tactic shots from the given list of sequences
        seq_shots = _get_shots(prj, seqs=used_seqs)

        #get shots that are both in Tactic and in the list of shots in the range
        seq_shots_set = set(seq_shots)
        matching_shots = codes.intersection(seq_shots_set)

        #return a sorted list of shots
        return sorted(list(matching_shots))



def _get_shots(prj, seqs=None, shot=None):
    """
    Query for shots.
    @param seqs A list of sequence codes to return a list of shots from.
    @param shot A shot to query in Tactic.
    @returns a list of shot codes matching the seqs and/or shots.
    """

    filters = [("project.Project.sg_code", "is", prj)]

    if shot:
        filters.append(("code", "is", shot))
    elif seqs:
        filters.append(("sg_sequence.Sequence.code", "in", seqs))

    columns = ["code"]

    shots = sg.find("Shot", filters, columns)

    if shots is None:
        return []

    return [ str(x["code"]) for x in shots ]

def split_expr(expr):
    """
    Split an expression string into elements.
    @param expr An expression string to split.
    @returns a tuple containing all expression elements.
    """
    return ( x.strip() for x in expr.split(EXPR_DELIMETER) )

def split_range(expr):
    """
    Split an expression range element.
    @param expr An expression string to split.
    @returns A tuple containing the left hand and right hand arugments of a range expression element.
    """
    return ( x.strip() for x in expr.split(EXPR_RANGE_CHAR) )


def _eval_expr_arg(expr_arg, prj=None, seq=None):
    """
    Evaluate a single expression argument.
    @param expr_arg A single expression argument.
    @param prj Tactic project code.
    @param seq Current Tactic sequence code.
    @returns a argument value dict containing the prj, seq and shot
    """
    shot_values = {"prj":prj, "seq":seq, "shot":None}

    #iterate over all expression patterns matching against the expression argument.
    for pattern in EXPR_PATTERNS:
        m = re.match(pattern, expr_arg)
        #if a pattern match is found, get the argument values
        if m:
            print "FOUND MATCH", pattern
            match = m.groupdict()
            if seq and match["seq"] != seq and match.get("shot", None) is None:
                match_shot = match.get("seq", None)
                match_seq = shot_values["seq"]
            else:
                match_shot = match.get("shot", None)
                match_seq = match.get("seq", None)

            shot_values["seq"] = match_seq
            shot_values["shot"] = match_shot

            print "------------------------------------<", shot_values
            return shot_values
    return None

def _eval_expr_element(expr_element, prj=None, seq=None):
    """
    Evaluate a single expression element.
    @param expr_element An expression element.
    @param prj Tactic project code.
    @param seq Current Tactic sequence code.
    @returns The current project, the current seq and a list of evaluated shots.
    """
    #if a shot range
    if EXPR_RANGE_CHAR in expr_element:
        start_shot = None
        end_shot = None

        lharg, rharg  = split_range(expr_element)

        range_start_vals = _eval_expr_arg(lharg, prj=prj, seq=seq)


        print "----------->", range_start_vals

        if range_start_vals is None:
            raise InvalidShotExprError("Unable to evaluate expression argument '%s'" % lharg)

        prj = range_start_vals["prj"]

        if prj is None:
            raise InvalidShotExprError("Unable to evaluate shot range element '%s'. "\
                "Unable to determine project." % expr_element)

        range_end_vals = _eval_expr_arg(rharg, prj=prj, seq=range_start_vals["seq"])

        print "----------->", range_end_vals

        if range_end_vals is None:
            raise InvalidShotExprError("Unable to evaluate expression argument '%s'" % rharg)

        seq = range_end_vals["seq"]

        try:
            range_shots = _eval_shot_range(range_start_vals, range_end_vals)
        except Exception, why:
            raise InvalidShotExprError("Unable to evaluate shot range element '%s'. %s" %
                    (expr_element, why))

        return prj, seq, range_shots

    else:

        arg_values = _eval_expr_arg(expr_element, prj=prj, seq=seq)

        if arg_values is None:
            raise InvalidShotExprError("Unable to evaluate expression argument '%s'" % expr_element)

        prj = arg_values["prj"]
        seq = arg_values["seq"]
        shot = arg_values["shot"]


        if prj is None:
            raise InvalidShotExprError("Unable to evaluate shot range element '%s'. "\
                "Unable to determine project." % expr_element)

        print prj, seq, shot

        shots = []

        if shot:
            shot = "%s_%s_%s" % (prj, seq, shot)
            shots = _get_shots(prj, shot=shot)
        else:
            if seq:
                shots = _get_shots(prj, seqs=["%s_%s" % (prj, seq)])
            else:
                shots = _get_shots(prj)


        return prj, seq, shots

def _eval_shot_range(start_values, end_values):
    """
    @param start_values The range start values dict.
    @param end_values The range end values dict.
    @returns A list of evaluated shots.
    """
    prj = start_values["prj"]

    start_seq = start_values["seq"]
    start_shot = start_values["shot"] or start_shot_value * SHOT_PADDING

    end_seq = end_values["seq"] or start_seq
    end_shot = end_values["shot"] or "9" * SHOT_PADDING


    print start_seq, end_seq, start_shot, end_shot

    return

    #cast the sequence/shot nums to ints for iterating over
    start_seq_num = int(start_seq)
    start_shot_num = int(start_shot)
    end_seq_num = int(end_seq)
    end_shot_num = int(end_shot)

    if end_seq_num < start_seq_num:
        raise Exception("Range start sequence greather than range end sequence.")

    if end_seq_num == start_seq_num and end_shot_num < start_shot_num:
        raise Exception("Range start shot greater than range end shot")

    codes = set()
    used_seqs = []

    #iterate over all sequence and shot numbers between the start and end range
    for seq_num in range(start_seq_num, end_seq_num + 1):
        seq = "%s_q%s" % (prj, str(seq_num).zfill(SEQ_PADDING))
        used_seqs.append(seq)

        if seq_num == start_seq_num:
            _start_shot_num = start_shot_num
        else:
            _start_shot_num = 0

        if seq_num == end_seq_num:
            _end_shot_num = end_shot_num
        else:
            _end_shot_num = int("9" * SHOT_PADDING)

        for shot_num in range(_start_shot_num, _end_shot_num + 1):
            shot_code = "%s_s%s" % (seq, str(shot_num).zfill(SHOT_PADDING))
            codes.add(shot_code)

    #get a list of all Tactic shots from the given list of sequences
    seq_shots = _get_shots(prj, seqs=used_seqs)

    #get shots that are both in Tactic and in the list of shots in the range
    seq_shots_set = set(seq_shots)
    matching_shots = codes.intersection(seq_shots_set)

    #return a sorted list of shots
    return sorted(list(matching_shots))

def eval_expr_string(expr_string, exclude_seq_shot=True):
    """
    Evaluate an expression string.
    @param expr_string An expression string
    @param returns A list of evaluated shots.
    @param exclude_seq_shot If True, do not include the s0000 shot in the returned list.
    """
    prj = "spk"
    seq = None

    expr_elements = split_expr(expr_string)

    expr_shots = []

    for expr_element in expr_elements:
        prj, seq, shots = _eval_expr_element(expr_element, prj=prj, seq=seq)
        expr_shots.extend(shots)

    shots = list(set(expr_shots))

    if exclude_seq_shot:
        shots = filter(lambda x : "s0000" not in x, shots)

    return sorted(shots)

def eval_expr_csv(csv_path, exclude_seq_shot=True):
    """
    Evaluate and expression CSV file.
    @param csv_path Full path to an expression csv file.
    @returns A list of evaluated shots.
    """
    csv_reader = csv.reader(open(csv_path, "r"))
    exprs = []
    for row in csv_reader:
        print row
        exprs.append(row[0])
    expr = ",".join(exprs)

    return eval_expr_string(expr, exclude_seq_shot=exclude_seq_shot)

def eval_expr(expr, exclude_seq_shot=True):
    """
    Evaluate an expression.
    @param expr An expression string or full path to a expression csv file
    @returns A list of evaluated shots.
    """
    if expr.endswith(".csv") or re.search(r"^[a-zA-Z]\:|^/", expr):
        return eval_expr_csv(expr, exclude_seq_shot=exclude_seq_shot)
    return eval_expr_string(expr, exclude_seq_shot=exclude_seq_shot)