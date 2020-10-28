from music21 import duration
from fractions import Fraction
import math


def get_correct_accidental(acc):
    if acc is None:
        return None
    else:
        return acc.alter


def get_type_number(gn):
    if is_grace(gn) and gn.duration.type == "zero":
        # because the MusicXML import seems bugged for grace notes, and set duration 0. Default 8 in this case
        return 8
    else:
        return duration.convertTypeToNumber(gn.duration.type)


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


########################### old functions to check


# def get_beamings(note_list):
#     _beam_list = []
#     for n in note_list:
#         if n.isRest:
#             _beam_list.append([])
#         else:
#             _beam_list.append(n.beams.getTypes())
#     return _beam_list


def get_ties(note_list):
    _general_ties_list = []
    for n in note_list:
        if n.tie == None:
            _general_ties_list.append(None)
        else:
            _general_ties_list.append(n.tie.type)
    # keep only the information of when a note is tied to the previous
    # (also we solve the bad notation of having a start and a not specified stop, that can happen in music21)
    _ties_list = [False] * len(_general_ties_list)
    for i, t in enumerate(_general_ties_list):
        if t == "start" and i < len(_ties_list) - 1:
            _ties_list[i + 1] = True
        elif t == "continue" and i < len(_ties_list) - 1:
            _ties_list[i + 1] = True
            if (
                i == 0
            ):  # we can have a continue in the first note if the tie is from the previous bar
                _ties_list[i] = True
        elif t == "stop":
            if (
                i == 0
            ):  # we can have a stop in the first note if the tie is from the previous bar
                _ties_list[i] = True
            else:
                # assert (_ties_list[i] == True) #removed to import wrong scores even if it vould be correct
                _ties_list[i] = True
    return _ties_list


# def get_dots(note_list):
#     return [n.duration.dots for n in note_list]


def get_durations(note_list):
    return [Fraction(n.duration.quarterLength) for n in note_list]


def get_norm_durations(note_list):
    dur_list = get_durations(note_list)
    if sum(dur_list) == 0:
        raise ValueError("It's not possible to normalize the durations if the sum is 0")
    return [d / sum(dur_list) for d in dur_list]  # normalize the duration


def get_tuplets_info(note_list):
    """create a list with the string that is on the tuplet bracket"""
    str_list = []
    for n in note_list:
        tuple_info_list_for_note = []
        for t in n.duration.tuplets:
            if (
                t.tupletNormalShow == "number" or t.tupletNormalShow == "both"
            ):  # if there is a notation like "2:3"
                new_info = str(t.numberNotesActual) + ":" + str(t.numberNotesNormal)
            else:  # just a number for the tuplets
                new_info = str(t.numberNotesActual)
            # if the brackets are drown explicitly, add B
            if t.bracket:
                new_info = new_info + "B"
            tuple_info_list_for_note.append(new_info)
        str_list.append(tuple_info_list_for_note)
    return str_list


# # now correct the missing of "start" and add "continue" for clarity
#     max_tupl_len = max([len(tuplets_list)])
#     for ii in range(max_tupl_len):
#         start_index = None
#         stop_index = None
#         for i, note_tuple in enumerate(tuplets_list):
#             if len(note_tuple) > ii:
#                 if note_tuple[ii] == "start":
#                     assert start_index is None
#                     start_index = ii
#                 elif note_tuple[ii] is None:
#                     if start_index is None:
#                         start_index = ii
#                         new_tuplets_list[i][ii] = "start"
#                     else:
#                         new_tuplets_list[i][ii] = "continue"
#                 elif note_tuple[ii] == "stop":
#                     start_index = None
#                 else:
#                     raise TypeError("Invalid tuplet type")
#     return new_tuplets_list

