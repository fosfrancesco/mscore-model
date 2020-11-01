import music21 as m21
import sys
from pathlib import Path
from fractions import Fraction as Fr
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


def test_simplify_label1():
    n1 = m21.note.Note("E--5")
    n1.duration.quarterLength = 3
    assert simplify_label([gn2label(n1)]) == "[E5bb]2*"


def test_simplify_label2():
    n1 = m21.note.Note("D4")
    n_grace = n1.getGrace()
    n2 = m21.note.Note("E#5")
    assert simplify_label([gn2label(n) for n in [n_grace, n2]]) == "[D4]4gn,[E5#]4"


def test_gn2label_musicxml1():
    score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
    measures = score.parts[0].getElementsByClass("Measure")
    # measure 0
    gns_m0 = measures[0].getElementsByClass("GeneralNote")
    label_gns_m0 = [gn2label(gn) for gn in gns_m0]
    expected_label_gns_m0 = [([{"npp": "G4", "alt": None, "tie": False}], 1, 0, False)]
    assert label_gns_m0 == expected_label_gns_m0
    # measure 1
    gns_m1 = measures[1].getElementsByClass("GeneralNote")
    label_gns_m1 = [gn2label(gn) for gn in gns_m1]
    expected_label_gns_m1 = [
        ([{"npp": "E4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "F4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "G4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "A4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "C5", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "B4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "A4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "G4", "alt": None, "tie": False}], 4, 0, False),
    ]
    assert label_gns_m1 == expected_label_gns_m1
    # measure 2
    gns_m2 = measures[2].getElementsByClass("GeneralNote")
    label_gns_m2 = [gn2label(gn) for gn in gns_m2]
    expected_label_gns_m2 = [
        ([{"npp": "F4", "alt": None, "tie": False}], 4, 1, False),
        ([{"npp": "E4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "F4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "G4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "B4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "B4", "alt": None, "tie": True}], 4, 0, False),
    ]
    assert label_gns_m2 == expected_label_gns_m2
    # measure 3
    gns_m3 = measures[3].getElementsByClass("GeneralNote")
    label_gns_m3 = [gn2label(gn) for gn in gns_m3]
    expected_label_gns_m3 = [
        ([{"npp": "E4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "F4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "G4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "A4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "C5", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "G4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "F4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "E4", "alt": None, "tie": False}], 4, 0, False),
    ]
    assert label_gns_m3 == expected_label_gns_m3
    # measure 4
    gns_m4 = measures[4].getElementsByClass("GeneralNote")
    label_gns_m4 = [gn2label(gn) for gn in gns_m4]
    expected_label_gns_m4 = [
        (
            [
                {"npp": "D4", "alt": None, "tie": False},
                {"npp": "F4", "alt": None, "tie": False},
                {"npp": "A4", "alt": None, "tie": False},
            ],
            4,
            0,
            False,
        ),
        (
            [
                {"npp": "D4", "alt": None, "tie": True},
                {"npp": "F4", "alt": None, "tie": True},
                {"npp": "A4", "alt": None, "tie": True},
            ],
            4,
            0,
            False,
        ),
        (
            [
                {"npp": "D4", "alt": None, "tie": False},
                {"npp": "F4", "alt": None, "tie": False},
                {"npp": "C5", "alt": None, "tie": False},
            ],
            4,
            0,
            False,
        ),
        (
            [
                {"npp": "C4", "alt": None, "tie": False},
                {"npp": "E4", "alt": None, "tie": False},
                {"npp": "C5", "alt": None, "tie": True},
            ],
            4,
            0,
            False,
        ),
    ]
    assert label_gns_m4 == expected_label_gns_m4
    # measure 5
    gns_m5 = measures[5].getElementsByClass("GeneralNote")
    label_gns_m5 = [gn2label(gn) for gn in gns_m5]
    expected_label_gns_m5 = [
        ("R", 4, 0, False),
        ([{"npp": "D4", "alt": None, "tie": False}], 4, 0, False),
        ("R", 4, 1, False),
        ([{"npp": "G4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "A4", "alt": None, "tie": False}], 4, 0, False),
        ("R", 4, 0, False),
        ([{"npp": "G4", "alt": None, "tie": False}], 4, 0, False),
    ]
    assert label_gns_m5 == expected_label_gns_m5


def test_gn2label_musicxml2():
    score = m21.converter.parse(str(Path("tests/test_musicxml/test_score2.musicxml")))
    measures = score.parts[0].getElementsByClass("Measure")
    # measure 3 (grace note)
    gns_m3 = measures[3].getElementsByClass("GeneralNote")
    label_gns_m3 = [gn2label(gn) for gn in gns_m3]
    expected_label_gns_m3 = [
        ([{"npp": "F4", "alt": None, "tie": False}], 4, 0, False),
        ([{"npp": "E4", "alt": None, "tie": False}], 4, 0, True),
        ([{"npp": "E4", "alt": None, "tie": False}], 4, 0, False),
        ("R", 2, 0, False),
    ]
    assert label_gns_m3 == expected_label_gns_m3


def test_beams_musicxml1():
    score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
    measures = score.parts[0].getElementsByClass("Measure")
    # measure 1
    gns_m1 = measures[1].getElementsByClass("GeneralNote")
    label_gns_m1 = [get_beams(gn) for gn in gns_m1]
    expected_label_gns_m1 = [
        [],
        ["start"],
        ["stop"],
        [],
        ["start", "start"],
        ["continue", "continue"],
        ["continue", "continue"],
        ["stop", "stop"],
    ]
    assert label_gns_m1 == expected_label_gns_m1

    # measure 2
    gns_m2 = measures[2].getElementsByClass("GeneralNote")
    label_gns_m2 = [get_beams(gn) for gn in gns_m2]
    expected_label_gns_m2 = [
        [],
        ["partial"],
        ["start"],
        ["continue", "start"],
        ["stop", "stop"],
        [],
    ]
    assert label_gns_m2 == expected_label_gns_m2

    # measure 5
    gns_m5 = measures[5].getElementsByClass("GeneralNote")
    label_gns_m5 = [get_beams(gn) for gn in gns_m5]
    expected_label_gns_m5 = [
        ["partial"],
        ["partial"],
        [],
        ["partial"],
        ["partial"],
        ["partial", "partial"],
        ["partial", "partial"],
    ]
    assert label_gns_m5 == expected_label_gns_m5


def test_get_tuplets_musicxml1():
    score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
    measures = score.parts[0].getElementsByClass("Measure")
    # measure 1
    gns_m3 = measures[3].getElementsByClass("GeneralNote")
    tuplet_gns_m3 = [get_tuplets(gn) for gn in gns_m3]
    expected_tuplet_gns_m3 = [
        [],
        ["start"],
        ["continue"],
        ["stop"],
        [],
        ["start"],
        ["continue"],
        ["stop"],
    ]
    assert tuplet_gns_m3 == expected_tuplet_gns_m3


def test_get_tuplets_musicxml2():
    score = m21.converter.parse(str(Path("tests/test_musicxml/test_score3.musicxml")))
    measures = score.parts[0].getElementsByClass("Measure")
    # measure 0
    gns_m1 = measures[0].getElementsByClass("GeneralNote")
    tuplet_gns_m1 = [get_tuplets(gn) for gn in gns_m1]
    expected_tuplet_gns_m1 = [
        ["start"],
        ["continue", "start"],
        ["continue", "continue"],
        ["stop", "stop"],
        [],
        [],
        [],
        [],
    ]
    assert correct_tuplet(tuplet_gns_m1) == expected_tuplet_gns_m1


def test_correct_tuplet():
    tuplet = [
        ["start"],
        ["continue", "continue"],
        ["continue", "continue"],
        ["stop", "stop"],
        [],
        [],
        [],
        [],
    ]
    expected = [
        ["start"],
        ["continue", "start"],
        ["continue", "continue"],
        ["stop", "stop"],
        [],
        [],
        [],
        [],
    ]
    assert correct_tuplet(tuplet) == expected

