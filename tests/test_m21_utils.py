import sys

sys.path.append("/mnt/c/Documents and Settings/fosca/Desktop/CNAM/score_model/")
import music21 as m21
from lib.m21utils import *


def test_is_tied1():
    n1 = m21.note.Note("F5")
    assert is_tied(n1) == False


def test_is_tied2():
    n1 = m21.note.Note("F5")
    n1.tie = m21.tie.Tie("start")
    assert is_tied(n1) == False


def test_is_tied3():
    n1 = m21.note.Note("F5")
    n1.tie = m21.tie.Tie("continue")
    assert is_tied(n1) == True


def test_is_tied4():
    n1 = m21.note.Note("F5")
    n1.tie = m21.tie.Tie("stop")
    assert is_tied(n1) == True


def test_get_correct_accidental1():
    acc = m21.pitch.Accidental("sharp")
    assert get_correct_accidental(acc) == 1


def test_get_correct_accidental2():
    acc = m21.pitch.Accidental("natural")
    assert get_correct_accidental(acc) == 0


def test_get_correct_accidental3():
    assert get_correct_accidental(None) is None


def test_gn2pitches_tuple1():
    n1 = m21.note.Note("F5")
    assert gn2pitches_tuple(n1) == [{"npp": "F5", "alt": None, "tie": False}]


def test_gn2pitches_tuple2():
    n1 = m21.note.Note("F5#")
    assert gn2pitches_tuple(n1) == [{"npp": "F5", "alt": 1, "tie": False}]


def test_gn2pitches_tuple3():
    n1 = m21.note.Note("d3")
    n2 = m21.note.Note("g3")
    n3 = m21.note.Note("e-3")
    n3.tie = m21.tie.Tie("stop")
    chord = m21.chord.Chord([n1, n2, n3])
    assert gn2pitches_tuple(chord) == [
        {"npp": "D3", "alt": None, "tie": False},
        {"npp": "E3", "alt": -1, "tie": True},
        {"npp": "G3", "alt": None, "tie": False},
    ]


def test_get_note_head1():
    n1 = m21.note.Note("E--5")
    n1.duration.quarterLength = 3.0
    assert get_note_head(n1) == 2


def test_get_note_head2():
    n1 = m21.note.Note("E--5")
    n1.duration.quarterLength = 0.25
    assert get_note_head(n1) == 4


def test_get_note_dots1():
    n1 = m21.note.Note("E--5")
    n1.duration.quarterLength = 3.0
    assert get_dots(n1) == 1


def test_get_note_dots2():
    n1 = m21.note.Note("E--5")
    n1.duration.quarterLength = 2
    assert get_dots(n1) == 0


def test_get_note_dots3():
    n1 = m21.note.Note("E--5")
    n1.duration.quarterLength = 1.75
    assert get_dots(n1) == 2


def test_grace_note1():
    n1 = m21.note.Note("E--5")
    n_grace = n1.getGrace()
    assert is_grace(n_grace)
    assert not is_grace(n1)


def test_gn2label():
    n1 = m21.note.Note("E--5")
    n1.duration.quarterLength = 3
    assert gn2label(n1) == ([{"npp": "E5", "alt": -2, "tie": False}], 2, 1, False)
