import music21 as m21
from fractions import Fraction
from .bar_trees import Root, NotationTree, InternalNode, LeafNode, timeline2rt
from .music_sequences import Event, Timeline
from .constant import REST_SYMBOL, CONTINUATION_SYMBOL
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
        return int(m21.duration.convertTypeToNumber(gn.duration.type))


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
    if type(gn.duration) is m21.duration.GraceDuration:
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
                elif note_tuple[ii] == "continue":
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


def correct_beamings(beamings_list, gn_list):
    """Correct the sequential beaming structure.

    In case of rests between two beamed notes, we will have a sequence of beamings [start], [partial], [stop].
    this function correct that specific case, putting a "continue" instead of partial.

    Args:
        beamings_list (list): the sequential structure of beamings

    Raises:
        TypeError: Other errors are presents in the input beaming_list.

    Returns:
        list: a corrected sequential structure for beamings.
    """
    new_beaming_list = copy.deepcopy(beamings_list)
    # find groups of consecutive rests (also of size 1)
    index_to_check = []
    start = -1
    end = -1
    for i, gn in enumerate(gn_list):
        if gn.isRest:
            if start == -1:  # first rest of the sequence
                start = i
                end = i
            else:  # multiple consecutive rests, update end
                end = i
        else:
            if (
                start != -1 and start != 0
            ):  # first note after a sequence of rests, and we don't consider rests at the beginning
                index_to_check.append((start - 1, end + 1))
                start = -1  # reset start
                end = -1  # reset end
            else:
                start = -1  # reset start
                end = -1  # reset end
    # now check if around the rests there are groups of beamed notes with start and end
    for i2check in index_to_check:
        max_beams = min(
            [len(beamings_list[i2check[0]]), len(beamings_list[i2check[1]])]
        )
        for i in range(max_beams):
            if (
                beamings_list[i2check[0]][i] == "start"
                or beamings_list[i2check[0]][i] == "continue"
            ) and (
                beamings_list[i2check[1]][i] == "stop"
                or beamings_list[i2check[1]][i] == "continue"
            ):
                # change the beam of the rests in between from partial to continue
                for ii in range(i2check[0] + 1, i2check[1]):
                    new_beaming_list[ii][i] = "continue"
    return new_beaming_list


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
        # correct in case of beamed rests problems
        seq_structure = correct_beamings(seq_structure, gn_list)
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


def m21_2_notationtree(gn_list, tree_type):
    """Generate a notation tree from a list of music21 general notes corresponding to the gns in a voice in a measure.

    Args:
        gn_list (list): a list of music21 GeneralNote objects
        tree_type (string): either "beamings" or "tuplets" 

    Returns:
        NotationTree : the notation tree (NT or TT)
    """
    # extract information from general note
    seq_structure, grouping_info = m21_2_seq_struct(gn_list, tree_type)
    leaf_label_list = [gn2label(gn) for gn in gn_list]
    # set the tree
    root = Root()
    _recursive_tree_generation(seq_structure, leaf_label_list, grouping_info, root, 0)
    return NotationTree(root, tree_type=tree_type)


def _recursive_tree_generation(
    seq_structure, leaf_label_list, grouping_info, local_root, depth
):
    """Recursive function to generate the notation tree, called from m21_2_notationtree()."""
    temp_int_node = None
    start_index = None
    stop_index = None
    for i, n in enumerate(seq_structure):
        if len(n[depth:]) == 0:  # no beaming/tuplets
            assert start_index is None, "no beaming/tuplets start_index "
            assert stop_index is None, "no beaming/tuplets stop_index "
            LeafNode(local_root, leaf_label_list[i])
        elif n[depth] == "partial":  # partial beaming (only for BTs)
            assert start_index is None, "partial beaming start_index "
            assert stop_index is None, "partial beaming stop_index "
            # there are more levels of beam otherwise we would be on the previous case
            temp_int_node = InternalNode(local_root, grouping_info[i][depth])
            _recursive_tree_generation(
                [n], [leaf_label_list[i]], [grouping_info[i]], temp_int_node, depth + 1,
            )
            temp_int_node = None
        elif n[depth] == "start":  # start of a beam/tuplet
            assert start_index is None, "start of a beam/tuplet start_index "
            assert stop_index is None, "start of a beam/tuplet stop_index "
            start_index = i
        elif n[depth] == "continue":
            assert start_index is not None, "continue start_index "
            assert stop_index is None, "continue stop_index "
        elif n[depth] == "stop":
            assert start_index is not None, "stop start_index "
            assert stop_index is None, "stop stop_index "
            stop_index = i
            temp_int_node = InternalNode(local_root, grouping_info[i][depth])
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


def nt2general_notes(nt, tt):
    """Generate a list of music21 generalNote from a couple (beaming tree, couple tree).

    WARNING: the attribute tie cannot be correctly set on the first note. 
    Remember to run the method set_ties() when the entire voice is ready.

    Args:
        nt (NotationTree): A notation tree of type "beamings"
        tt (NotationTree): A notation tree of type "tuplets"

    Returns:
        list: a list of music21 GeneralNote
    """
    beamings = nt2seq_structure(nt)[0]
    tuplets, tuplets_info = nt2seq_structure(tt)
    labels = [n.label for n in nt.get_leaf_nodes()]

    gn_list = []

    for i, l in enumerate(labels):
        if l[0] == "R":  # rest
            gn = m21.note.Rest()
        elif len(l[0]) == 1:  # note
            gn = m21.note.Note(l[0][0]["npp"])
            if not l[0][0]["acc"] is None:
                acc = m21.pitch.Accidental(l[0][0]["acc"])
                gn.pitch.accidental = acc
        else:  # chord
            gn = m21.chord.Chord([p["npp"] for p in l[0]])
            for i, pitch in enumerate(l[0]):  # add accidentals
                if not pitch["acc"] is None:
                    acc = m21.pitch.Accidental(pitch["acc"])
                    gn.pitches[i].accidental = acc
        # set the eventual grace note
        if l[3]:
            gn = gn.getGrace()
        gn_list.append(gn)

    # add duration type
    for i, gn in enumerate(gn_list):
        if (
            labels[i][1] <= 2
        ):  # if the note is half or whole, it depends just on note type
            gn.duration.type = m21.duration.typeFromNumDict[labels[i][1]]
        else:  # if note-head >= 4, duration type depends on beamings
            gn.duration.type = m21.duration.typeFromNumDict[4 * (2 ** len(beamings[i]))]

    # add dots
    for i, gn in enumerate(gn_list):
        gn.duration.dots = labels[i][2]

    # add beamings
    for i, gn in enumerate(gn_list):
        if not gn.isRest:  # rests do not have beams in m21
            if not all(
                [b == "partial" for b in beamings[i]]
            ):  # this case is handled by note type only in m21
                for beam in beamings[i]:
                    if (beam == "start") or (beam == "stop") or ((beam == "continue")):
                        gn.beams.append(beam)
                    elif (
                        beam == "partial"
                    ):  # for partial, check the other beams to know if it is right or left
                        if any([b == "start" for b in beamings[i]]):
                            gn.beams.append("partial", "right")
                        else:
                            gn.beams.append("partial", "left")

    # add tuplets
    for i, gn in enumerate(gn_list):
        for ii, t in enumerate(tuplets[i]):
            t = m21tuple_from_info(tuplets_info[i][ii])
            # set the start and stop. Continue is None for m21 tuple and we don't need to set it
            if tuplets[i][ii] != "continue":
                t.type = tuplets[i][ii]
            gn.duration.appendTuplet(t)

    # add ties
    # there is a problems because m21 require a tie "start" and "continue" and we only have tie "stop"
    # we have to do this ideally when the entire score is complete
    gn_list = set_ties(gn_list, labels)

    return gn_list


def set_ties(gn_list, labels):
    for i, gn in enumerate(gn_list):
        if i > 0:  # can't set a stop on the first note
            previous_notes_to_set = []
            if gn.isRest:
                pass  # no ties on rests
            elif gn.isNote:
                if labels[i][0][0]["tie"]:
                    gn.tie = m21.tie.Tie("stop")
                    previous_notes_to_set.append(gn.nameWithOctave)
            elif gn.isChord:
                for ii, note in enumerate(gn):
                    if labels[i][0][ii]["tie"]:
                        note.tie = m21.tie.Tie("stop")
                        previous_notes_to_set.append(note.nameWithOctave)

            # correctly set the previous element if there was at least one tie
            if len(previous_notes_to_set) > 0:
                if gn_list[i - 1].isRest:
                    pass
                elif gn_list[i - 1].isNote:
                    assert len(previous_notes_to_set) == 1
                    assert gn.nameWithOctave == previous_notes_to_set[0]
                    if gn_list[i - 1].tie is None:  # there was not already a tie
                        gn_list[i - 1].tie = m21.tie.Tie("start")
                    else:
                        gn_list[i - 1].tie = m21.tie.Tie("continue")
                elif gn.isChord:
                    for note_name in previous_notes_to_set:
                        if (
                            gn_list[i - 1][note_name].tie is None
                        ):  # there was not already a tie
                            gn_list[i - 1][note_name].tie = m21.tie.Tie("start")
                        else:
                            gn_list[i - 1][note_name].tie = m21.tie.Tie("continue")

    return gn_list


def m21tuple_from_info(tuplet_info):
    """Generate a m21.duration.Tuplet object from our string description (for a single general note).

    Examples are "3B", "3:2", "5:4B" where the B means that the bracket is displayed.

    Args:
        tuplet_info (string): the description of the tuplet for a single general note

    Returns:
        m21.duration.Tuplet: the m21 tuplet object
    """
    bracket = tuplet_info.endswith("B")
    if bracket:
        tuplet_info = tuplet_info[:-1]
    # set the notation "a" or "a:b"
    if len(tuplet_info.split(":")) == 1:
        t = m21.duration.Tuplet(int(tuplet_info), 2)
        t.tupletActualShow = "number"
        t.tupletNormalShow = None
    else:
        info = tuplet_info.split(":")
        t = m21.duration.Tuplet(int(info[0]), int(info[1]))
        t.tupletActualShow = "number"
        t.tupletNormalShow = "number"
    # set if the bracket is visible
    t.bracket = bracket
    return t


def m21_2_timeline(gn_list):
    # create the events
    events = [
        Event(gn.offset, REST_SYMBOL)
        if gn.isRest
        else Event(gn.offset, [p.midi for p in gn.pitches])
        for gn in gn_list
    ]
    return Timeline(
        events,
        start=0,
        end=sum([Fraction(gn.duration.quarterLength) for gn in gn_list]),
    )


def m21_2_rhythmtree(
    gn_list, allowed_divisions=[2, 3], max_depth=7, div_preferences=None
):
    # create the timeline
    tim = m21_2_timeline(gn_list)
    return timeline2rt(tim, allowed_divisions, max_depth, div_preferences)


def reconstruct(score):
    """ This function ensures that the score is systematically of the structure : Score -> Part -> Measure -> Voice
    It recursively goes through the whole score, if the type of stream is not as expected,
    a new stream is inserted.

    Args: score (m21.stream) : a stream of m21 objects

    """
    empty = True

    # determine the expected type of stream, depending on the current stream
    if isinstance(score, m21.stream.Score):
        expected_type = m21.stream.Part
    elif isinstance(score, m21.stream.Part):
        expected_type = m21.stream.Measure
    elif isinstance(score, m21.stream.Measure):
        expected_type = m21.stream.Voice
    else:
        return

    # iterate through only Streams and Notes, this ensures everything else stays in the right place
    iterator = score.getElementsByClass([m21.stream.Stream, m21.note.GeneralNote])
    stream = m21.stream.Stream()

    # if the item in the iterator is not of the expexted type :
    # it is added to temporary stream, from which the new node will be initialized
    for item in iterator:
        if not isinstance(item, expected_type):
            empty = False
            stream.append(item)
            score.remove(item)
        reconstruct(item)

    # if a gap was found, create the stream, and add to the score
    if not empty:
        new_node = expected_type(stream)
        score.append(new_node)
        # the new node must be also reconstructed in case there's more than one gap
        # (for ex: a score with only notes)
        reconstruct(new_node)


class Voice(m21.stream.Voice):
    def __init__(self, stream):
        m21.stream.Voice.__init__(self, stream, id=stream.id)
        self.beaming_tree = m21_2_notationtree(stream, "beamings")
        self.tuplet_tree = m21_2_notationtree(stream, "tuplets")


def score_notation_tree(score):
    """Replaces the voices with score model voices"""
    for el in score.recurse():
        if isinstance(el, m21.stream.Voice):
            print(el)
            new_voice = Voice(el)
            score.replace(el, new_voice, recurse=True)


def model_score(score):
    """Takes any m21 score, reorganizes it, and compute notation trees"""
    reconstruct(score)
    score_notation_tree(score)
    _test_model_score(score)
    return score


def _test_model_score(score):
    error = "Model Score Error : "
    if isinstance(score, m21.stream.Score):
        assert len(score.getElementsByClass("Part")) > 0, (
            error + "The score has no parts"
        )
    elif isinstance(score, m21.stream.Part):
        assert len(score.getElementsByClass("Measure")) > 0, (
            error + "The part has no measures"
        )
    elif isinstance(score, m21.stream.Measure):
        assert len(score.getElementsByClass("Voice")) > 0, (
            error + "The measure has no voices"
        )
    else:
        return

    iterator = score.getElementsByClass([m21.stream.Stream, m21.note.GeneralNote])

    for item in iterator:
        if isinstance(score, m21.stream.Measure):
            assert isinstance(item, Voice), (
                error + "Wrong voice class type" + str(type(item))
            )
        _test_model_score(item)
