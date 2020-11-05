from music21 import duration
from fractions import Fraction
import lib.NotationTree as nt
import math
import copy
from itertools import islice


## functions to extract descriptors from music21 to create Notation Trees


def get_accidental_number(acc):
    """Get an integer from a music21 accidental (e.g. # is +1 and bb is -2)."""
    if acc is None:
        return None
    else:
        return int(acc.alter)


def get_type_number(gn):
    """Get the music21 type number for a generalnote (and correct an MusicXML import problem by setting a default)."""
    if is_grace(gn) and gn.duration.type == "zero":
        # because the MusicXML import seems bugged for grace notes, and set duration 0. Default 8 in this case
        return 8
    else:
        return int(duration.convertTypeToNumber(gn.duration.type))


def get_note_head(gn):
    """Get a number encoding the note-head.
    
    A note-head is encoded as an integer, where 4,2,1 encode respectively a quarter note, a half note and a whole note.
    Shorter durations are not encoded in the head (but in beamings and tuplets).
    Rests are considered as notes for simplicity, i.e. there is not type 8, even if it exist a different head symbol for rests.

    Args:
        gn (GeneralNote): a music21 general note

    Returns:
        int: the integer encoding the note-head
    """
    type_number = get_type_number(gn)
    if type_number >= 4:
        return 4
    else:
        return type_number


def is_tied(note):
    """Get a boolean from a general note saying if it is tied to the previous gnote."""
    if note.tie is not None and (
        note.tie.type == "stop" or note.tie.type == "continue"
    ):
        return True
    else:
        return False


def is_grace(gn):
    """Get a boolean from a general note saying if it is a grace note."""
    if type(gn.duration) is duration.GraceDuration:
        return True
    else:
        return False


def get_dots(gn):
    """Get the number of dots from a general note."""
    return gn.duration.dots


def gn2pitches_list(gn):
    """Get the list of pitches in a general note.

    Pitches is a list where each element is a dictionary with keys: "npp" (string): natural pitch position (the pitch without accidentals), 
    "acc" (int) : accidentals (e.g. # is +1 and bb is -1), "tie" (bool): if the gnote is tied to the precedent gnote.

    Args:
        gn (GeneralNote): the music21 general note.

    Returns:
        list: a list of dictionaries representing pitches.
    """
    if gn.isRest:
        return "R"
    else:
        if gn.isChord:
            out = []
            for n in sorted(gn.notes):
                out.append(
                    {
                        "npp": n.pitch.step + str(n.pitch.octave),
                        "acc": get_accidental_number(n.pitch.accidental),
                        "tie": is_tied(n),
                    }
                )
            return out
        elif gn.isNote:
            return [
                {
                    "npp": gn.pitch.step + str(gn.pitch.octave),
                    "acc": get_accidental_number(gn.pitch.accidental),
                    "tie": is_tied(gn),
                }
            ]


def gn2label(gn):
    """Get a label that uniquely identify a general note (not considering tuplets or beamings).

    The label is a tuple of length 4 that contains: pitches (list), note-head (integer), dots (integer) and grace-note (bool).

    Args:
        gn (Generalnote): the music21 general note (e.g. note, rest or chord).

    Returns:
        tuple: the label.
    """
    return (gn2pitches_list(gn), get_note_head(gn), get_dots(gn), is_grace(gn))


def get_beams(gn):
    """Return the (part of) beamings on top of a general note.

    The beamings are expressed as a list of strings "start", "continue" and "stop.

    Args:
        gn (GeneralNote): the music21 general note (e.g. note, rest or chord).

    Returns:
        list: the list of beamings.
    """
    beam_list = []
    if not gn.isRest:
        beam_list.extend(gn.beams.getTypes())

    if len(beam_list) == 0:  # add informations for rests and notes not grouped
        for __ in range(int(math.log(get_type_number(gn) / 4, 2))):
            beam_list.append("partial")

    return beam_list


def get_tuplets(gn):
    """Return the (part of) tuplets on top of a general note.

    The tuplets are expressed as a list of strings "start", "continue" and "stop.

    Args:
        gn (GeneralNote): the music21 general note (e.g. note, rest or chord).

    Returns:
        list: the list of tuplets.
    """
    tuplets_list = [t.type for t in gn.duration.tuplets]
    # substitute None with continue
    return ["continue" if t is None else t for t in tuplets_list]


def correct_tuplet(tuplets_list):
    """Correct the sequential tuplet structure.

    It seems that the import from musicxml in music21 set some "start" elements as None (that is then converted in "continue" in our representation).
    This function handle this problem setting it back to "start".

    Args:
        tuplets_list (list): the sequential structure of tuplets

    Raises:
        TypeError: Other errors are presents in the input tuplet_list.

    Returns:
        list: a corrected sequential structure for tuplets.
    """
    new_tuplets_list = copy.deepcopy(tuplets_list)
    # correct the wrong xml import where some start are substituted by None
    max_tupl_len = max([len(tuplets_list)])
    for ii in range(max_tupl_len):
        start_index = None
        for i, note_tuple in enumerate(tuplets_list):
            if len(note_tuple) > ii:
                if note_tuple[ii] == "start":
                    assert start_index is None
                    start_index = ii
                elif note_tuple[ii] is "continue":
                    if start_index is None:
                        start_index = ii
                        new_tuplets_list[i][ii] = "start"
                    else:
                        new_tuplets_list[i][ii] = "continue"
                elif note_tuple[ii] == "stop":
                    start_index = None
                else:
                    raise TypeError("Invalid tuplet type")
    return new_tuplets_list


def m21_2_seq_struct(gn_list, struct_type):
    """Generate a sequential representation of the structure (beamings and tuplets) from the general notes in a single measure (and a single voice).

    The function gives two outputs: seq_structure and internal_nodes info. 
    The latter contains the tuplet numbers, but it is still present for beamings as empty list of lists.

    Args:
        gn_list (list of generalNotes): a list of music21 general notes in a measure (and a single voice)
        struct_type (string): either "beamings" or "tuplets"

    Raises:
        TypeError: if struct_type is not "beamings" nor "tuplets"

    Returns:
        couple: (seq_structure, grouping_info)
    """
    if struct_type == "beamings":
        seq_structure = [get_beams(gn) for gn in gn_list]
        grouping_info = [
            ["" for ee in e] for e in seq_structure
        ]  # useless for beamings
    elif struct_type == "tuplets":
        seq_structure = [get_tuplets(gn) for gn in gn_list]
        seq_structure = correct_tuplet(
            seq_structure
        )  # correct in case of XML import problems
        grouping_info = [get_tuplets_info(gn) for gn in gn_list]
    else:
        raise TypeError("Only beamings and tuplets are allowed types")
    return seq_structure, grouping_info


def accidental2string(acc_number):
    """Return a string repr of accidentals."""
    if acc_number is None:
        return ""
    elif acc_number > 0:
        return "#" * int(acc_number)
    elif acc_number < 0:
        return "b" * int(abs(acc_number))
    else:
        return "n"


def tie2string(tie):
    """Return a string repr of a tie."""
    if tie:
        return "T"
    else:
        return ""


def dot2string(dot):
    """Return a string repr of dots."""
    return "*" * int(dot)


def gracenote2string(gracenote):
    """Return a string repr of a gracenote."""
    if gracenote:
        return "gn"
    else:
        return ""


def simplify_label(label):
    """Create a simple string representation of the notation tree leaf node labels for a better visualization.

    Args:
        label (tuple): the label of a leaf node in a notation tree

    Returns:
        string: a simple but still unique representation of the leaf
    """
    # return a simpler label version
    if label[0] == "R":
        out = "R"
    else:
        out = "["
        for pitch in label[0]:
            out += "{}{}{},".format(
                pitch["npp"], accidental2string(pitch["acc"]), tie2string(pitch["tie"]),
            )
        out = out[:-1]  # remove last comma
        out += "]"
    out += "{}{}{}".format(label[1], dot2string(label[2]), gracenote2string(label[3]))
    return out


def m21_2_notationtree(gn_list, tree_type):
    """Generate a notation tree from a list of music21 general notes corresponding to the gns in a voice in a measure.

    Args:
        gn_list (list): a list of music21 GeneralNote objects
        tree_type (string): either "beamings" or "tuplets" 

    Returns:
        NotationTree : the notation tree (BT or TT)
    """
    # extract information from general note
    seq_structure, grouping_info = m21_2_seq_struct(gn_list, tree_type)
    leaf_label_list = [gn2label(gn) for gn in gn_list]
    # set the tree
    root = nt.Root()
    _recursive_tree_generation(seq_structure, leaf_label_list, grouping_info, root, 0)
    return nt.NotationTree(root, tree_type=tree_type)


def _recursive_tree_generation(
    seq_structure, leaf_label_list, grouping_info, local_root, depth
):
    """Recursive function to generate the notation tree, called from m21_2_notationtree()."""
    temp_int_node = None
    start_index = None
    stop_index = None
    for i, n in enumerate(seq_structure):
        if len(n[depth:]) == 0:  # no beaming/tuplets
            assert start_index is None
            assert stop_index is None
            nt.LeafNode(local_root, leaf_label_list[i])
        elif n[depth] == "partial":  # partial beaming (only for BTs)
            assert start_index is None
            assert stop_index is None
            # there are more levels of beam otherwise we would be on the previous case
            temp_int_node = nt.InternalNode(local_root, grouping_info[i][depth])
            _recursive_tree_generation(
                [n], [leaf_label_list[i]], [grouping_info[i]], temp_int_node, depth + 1,
            )
            temp_int_node = None
        elif n[depth] == "start":  # start of a beam/tuplet
            assert start_index is None
            assert stop_index is None
            start_index = i
        elif n[depth] == "continue":
            assert start_index is not None
            assert stop_index is None
        elif n[depth] == "stop":
            assert start_index is not None
            assert stop_index is None
            stop_index = i
            temp_int_node = nt.InternalNode(local_root, grouping_info[i][depth])
            _recursive_tree_generation(
                seq_structure[start_index : stop_index + 1],
                leaf_label_list[start_index : stop_index + 1],
                grouping_info[start_index : stop_index + 1],
                temp_int_node,
                depth + 1,
            )
            # reset the variables
            temp_int_node = None
            start_index = None
            stop_index = None


def get_tuplets_info(gn):
    """Create a list with the string that is on the tuplet bracket."""
    tuple_info = []
    for t in gn.duration.tuplets:
        if (
            t.tupletNormalShow == "number" or t.tupletNormalShow == "both"
        ):  # if there is a notation like "2:3"
            new_info = str(t.numberNotesActual) + ":" + str(t.numberNotesNormal)
        else:  # just a number for the tuplets
            new_info = str(t.numberNotesActual)
        # if the brackets are drown explicitly, add B
        if t.bracket:
            new_info = new_info + "B"
        tuple_info.append(new_info)
    return tuple_info


## functions to extract descriptors from Notation Trees to create music21


def nt2inter_gn_groupings(nt):
    """Return the number of grouping ``between'' two adjacent notes.

    For beamings trees this is the number of beams connecting two adjacent notes.

    Args:
        nt (NotationTree): A notation tree, either beaming tree or tuplet tree.

    Returns:
        list: A list of length [number_of_leaves - 1], with integers.
    """
    leaves = nt.get_leaf_nodes()
    # find the connections between 2 adjacent leaves
    leaves_connection = [nt.get_lca(n1, n2) for n1, n2 in window(leaves)]
    return [nt.get_depth(n) for n in leaves_connection]


def nt2over_gn_groupings(nt):
    """Return the number of grouping ``over'' a note.

    For beamings trees this is the number of beams over each note.

    Args:
        nt (NotationTree): A notation tree, either beaming tree or tuplet tree.

    Returns:
        list: A list of length [number_of_leaves], with integers.
    """
    leaves = nt.get_leaf_nodes()
    # find the leaves depths in the tree
    leaves_depths = [nt.get_depth(leaf) for leaf in leaves]
    return [d - 1 for d in leaves_depths]


def nt2seq_structure(nt):
    """Create the sequential representation of groupings from a notation tree (hierarchical representation).

    In particular the functions generates two outputs.
    seq_structure : a nested list of length [number_of_leaves] in the nt, with "start","stop" and "continue" elements depending on the tree structure;
    grouping_info : a nested list of length [number_of_leaves] with the grouping info.
    The latter corresponds for tuplets to the tuplet name in the bracket (and B if the bracket is visible),
    but it is computed also for beamings, as list of empty strings, to preserve the similarity.

    Args:
        nt (NotationTree): A notation tree, either beaming tree or tuplet tree.

    Returns:
        couple: (seq_structure,grouping_info)
    """

    def _nt2seq_structure(node):
        if node.type == "leaf":
            return [[]], [[]]
        else:
            subtree_leaves = nt.get_leaf_nodes(local_root=node)
            if len(subtree_leaves) > 1:
                structure = (
                    [["start"]]
                    + [["continue"] for _ in subtree_leaves[1:-1]]
                    + [["stop"]]
                )
                info = [[str(node.label)] for _ in subtree_leaves]
            else:
                structure = [["partial"]]
                info = [[str(node.label)]]

            offset = 0
            for child in node.children:
                low_struct, low_info = _nt2seq_structure(child)
                for st, inf in zip(low_struct, low_info):
                    structure[offset].extend(st)
                    info[offset].extend(inf)
                    offset += 1
            return structure, info

    seq_structure = [[] for _ in nt.get_leaf_nodes()]
    grouping_info = [[] for _ in nt.get_leaf_nodes()]
    offset = 0
    for child in nt.root.children:
        low_struct, low_info = _nt2seq_structure(child)
        for st, inf in zip(low_struct, low_info):
            seq_structure[offset].extend(st)
            grouping_info[offset].extend(inf)
            offset += 1

    return seq_structure, grouping_info


def window(seq, n=2):
    """Return a sliding window (of width n) over data."""
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def nt2general_notes(bt, tt):
    beamings = nt2seq_structure(bt)[0]
    tuplets, tuplets_info = nt2seq_structure(tt)
    labels = [n.label for n in bt.get_leaf_nodes()]


########################### old functions to check


# def get_beamings(note_list):
#     _beam_list = []
#     for n in note_list:
#         if n.isRest:
#             _beam_list.append([])
#         else:
#             _beam_list.append(n.beams.getTypes())
#     return _beam_list


# def get_dots(note_list):
#     return [n.duration.dots for n in note_list]


# def get_durations(note_list):
#     return [Fraction(n.duration.quarterLength) for n in note_list]


# def get_norm_durations(note_list):
#     dur_list = get_durations(note_list)
#     if sum(dur_list) == 0:
#         raise ValueError("It's not possible to normalize the durations if the sum is 0")
#     return [d / sum(dur_list) for d in dur_list]  # normalize the duration

