from music21 import duration
from fractions import Fraction
import lib.NotationTree as nt
import math
import copy
from itertools import islice


## functions to extract descriptors from music21 to create Notation Trees


def get_correct_accidental(acc):
    if acc is None:
        return None
    else:
        return int(acc.alter)


def get_type_number(gn):
    if is_grace(gn) and gn.duration.type == "zero":
        # because the MusicXML import seems bugged for grace notes, and set duration 0. Default 8 in this case
        return 8
    else:
        return int(duration.convertTypeToNumber(gn.duration.type))


def get_note_head(gn):
    # Get a number equivalent to the note head, e.g. 4,2,1. Shorter durations are not visible in the head
    # Rests are considered as notes for simplicity, i.e. there is not type 8, even if it exist a different head symbol for rests
    type_number = get_type_number(gn)
    if type_number >= 4:
        return 4
    else:
        return type_number


def is_tied(note):
    # return True if a note is tied with the previous one
    if note.tie is not None and (
        note.tie.type == "stop" or note.tie.type == "continue"
    ):
        return True
    else:
        return False


def is_grace(gn):
    if type(gn.duration) is duration.GraceDuration:
        return True
    else:
        return False


def get_dots(gn):
    return gn.duration.dots


def gn2pitches_tuple(gn):
    if gn.isRest:
        return "R"
    else:
        if gn.isChord:
            out = []
            for n in sorted(gn.notes):
                out.append(
                    {
                        "npp": n.pitch.step + str(n.pitch.octave),
                        "alt": get_correct_accidental(n.pitch.accidental),
                        "tie": is_tied(n),
                    }
                )
            return out
        elif gn.isNote:
            return [
                {
                    "npp": gn.pitch.step + str(gn.pitch.octave),
                    "alt": get_correct_accidental(gn.pitch.accidental),
                    "tie": is_tied(gn),
                }
            ]


def gn2label(gn):
    return (gn2pitches_tuple(gn), get_note_head(gn), get_dots(gn), is_grace(gn))


def get_beams(gn):
    beam_list = []
    if not gn.isRest:
        beam_list.extend(gn.beams.getTypes())

    if len(beam_list) == 0:  # add informations for rests and notes not grouped
        for __ in range(int(math.log(get_type_number(gn) / 4, 2))):
            beam_list.append("partial")

    return beam_list


def get_tuplets(gn):
    tuplets_list = [t.type for t in gn.duration.tuplets]
    # substitute None with continue
    return ["continue" if t is None else t for t in tuplets_list]


def correct_tuplet(tuplets_list):
    new_tuplets_list = copy.deepcopy(tuplets_list)
    # correct the wrong xml import where some start are substituted by None
    max_tupl_len = max([len(tuplets_list)])
    for ii in range(max_tupl_len):
        start_index = None
        stop_index = None
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
    """Generate a sequential representation of the structure (beamings and tuplets) from the general notes in a single measure (and a single voice)
    The function gives two outputs: seq_structure and internal_nodes info.
    The latter contains the tuplet numbers, but it is still present for beamings as empty list of lists

    Args:
        gn_list (list of generalNotes): a list of music21 general notes in a measure (and a single voice)
        struct_type (string): either "beamings" or "tuplets"

    Raises:
        TypeError: if struct_type is not "beamings" nor "tuplets"

    Returns:
        couple: (seq_structure, internal_nodes_info)
    """
    if struct_type == "beamings":
        seq_structure = [get_beams(gn) for gn in gn_list]
        internal_nodes_info = [
            ["" for ee in e] for e in seq_structure
        ]  # useless for beamings
    elif struct_type == "tuplets":
        seq_structure = [get_tuplets(gn) for gn in gn_list]
        seq_structure = correct_tuplet(
            seq_structure
        )  # correct in case of XML import problems
        internal_nodes_info = [get_tuplets_info(gn) for gn in gn_list]
    else:
        raise TypeError("Only beamings and tuplets are allowed types")
    return seq_structure, internal_nodes_info


def alteration2string(alt_number):
    """
    Return a text repr of accidentals
    """
    if alt_number is None:
        return ""
    elif alt_number > 0:
        return "#" * int(alt_number)
    elif alt_number < 0:
        return "b" * int(abs(alt_number))
    else:
        return "n"


def tie2string(tie):
    if tie:
        return "T"
    else:
        return ""


def dot2string(dot):
    return "*" * int(dot)


def gracenote2string(gracenote):
    if gracenote:
        return "gn"
    else:
        return ""


def simplify_label(label):
    # return a simpler label version
    if label[0] == "R":
        out = "R"
    else:
        out = "["
        for pitch in label[0]:
            out += "{}{}{},".format(
                pitch["npp"], alteration2string(pitch["alt"]), tie2string(pitch["tie"]),
            )
        out = out[:-1]  # remove last comma
        out += "]"
    out += "{}{}{}".format(label[1], dot2string(label[2]), gracenote2string(label[3]))
    return out


def ntfromm21(gn_list, tree_type):
    # extract information from general note
    seq_structure, internal_nodes_info = m21_2_seq_struct(gn_list, tree_type)
    leaf_label_list = [gn2label(gn) for gn in gn_list]
    # set the tree
    root = nt.Root()
    _recursive_tree_generation(
        seq_structure, leaf_label_list, internal_nodes_info, root, 0
    )
    return nt.NotationTree(root, tree_type=tree_type)


def _recursive_tree_generation(
    seq_structure, leaf_label_list, internal_nodes_info, local_root, depth
):
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
            temp_int_node = nt.InternalNode(local_root, internal_nodes_info[i][depth])
            _recursive_tree_generation(
                [n],
                [leaf_label_list[i]],
                [internal_nodes_info[i]],
                temp_int_node,
                depth + 1,
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
            temp_int_node = nt.InternalNode(local_root, internal_nodes_info[i][depth])
            _recursive_tree_generation(
                seq_structure[start_index : stop_index + 1],
                leaf_label_list[start_index : stop_index + 1],
                internal_nodes_info[start_index : stop_index + 1],
                temp_int_node,
                depth + 1,
            )
            # reset the variables
            temp_int_node = None
            start_index = None
            stop_index = None


def get_tuplets_info(gn):
    """create a list with the string that is on the tuplet bracket"""
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
    leaves = nt.get_leaf_nodes()
    # find the connections between 2 adjacent leaves
    leaves_connection = [nt.get_lca(n1, n2) for n1, n2 in window(leaves)]
    return [nt.get_depth(n) for n in leaves_connection]


def nt2over_gn_groupings(nt):
    leaves = nt.get_leaf_nodes()
    # find the leaves depths in the tree
    leaves_depths = [nt.get_depth(leaf) for leaf in leaves]
    return [d - 1 for d in leaves_depths]


def nt2seq_structure(nt):
    def _nt2seq_structure(node):
        if node.type == "leaf":
            return [[]]
        else:
            subtree_leaves = nt.get_leaf_nodes(local_root=node)
            if len(subtree_leaves) > 1:
                structure = (
                    [["start"]]
                    + [["continue"] for _ in subtree_leaves[1:-1]]
                    + [["stop"]]
                )
            else:
                structure = [["partial"]]

            offset = 0
            for child in node.children:
                low_struct = _nt2seq_structure(child)
                for s in low_struct:
                    structure[offset].extend(s)
                    offset += 1
            return structure

    seq_structure = [[] for _ in nt.get_leaf_nodes()]
    offset = 0
    for child in nt.root.children:
        low_struct = _nt2seq_structure(child)
        for s in low_struct:
            seq_structure[offset].extend(s)
            offset += 1

    return seq_structure

    # # fill the first element (only starts allowed)
    # for cd in range(connection_depth[0]):
    #     seq_structure[0][cd] = "start"
    # # fill the elements in the middle
    # max_conn_depth = max(connection_depth)
    # for i, c in enumerate(connection_depth):
    #     if i > 0:  # cases handled separately
    #         for ii in range(c):
    #             # fill according to the previous element
    #             if ii + 1 == connection_depth[i - 1]:
    #                 seq_structure[i][ii] = "continue"
    #             elif ii + 1 > connection_depth[i - 1]:
    #                 seq_structure[i][ii] = "start"
    #         if c < connection_depth[i - 1]:
    #             for ii in range(connection_depth[i - 1]):
    #                 seq_structure[i][ii] = "stop"
    # # fill the last element (only stops allowed)
    # for cd in range(connection_depth[-1]):
    #     seq_structure[-1][cd] = "stop"


def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


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


def get_durations(note_list):
    return [Fraction(n.duration.quarterLength) for n in note_list]


def get_norm_durations(note_list):
    dur_list = get_durations(note_list)
    if sum(dur_list) == 0:
        raise ValueError("It's not possible to normalize the durations if the sum is 0")
    return [d / sum(dur_list) for d in dur_list]  # normalize the duration

