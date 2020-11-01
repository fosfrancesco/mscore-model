from lib.m21utils import gn2label
import music21 as m21
from pathlib import Path
from fractions import Fraction as Fr

from lib.NotationTree import *


def test_notenode1():
    n1 = m21.note.Note("E--5")
    n1.duration.quarterLength = 3
    n2 = m21.note.Note("D4")
    n_grace = n2.getGrace()
    root = Root()
    node1 = LeafNode(root, [gn2label(gn) for gn in [n_grace, n1]])
    assert node1.label == [
        ([{"npp": "D4", "alt": None, "tie": False}], 4, 0, True),
        ([{"npp": "E5", "alt": -2, "tie": False}], 2, 1, False),
    ]
    assert str(node1) == str(
        [
            ([{"npp": "D4", "alt": None, "tie": False}], 4, 0, True),
            ([{"npp": "E5", "alt": -2, "tie": False}], 2, 1, False),
        ]
    )


def test_internalnode1():
    root = Root()
    node1 = InternalNode(root, True)
    node3 = InternalNode(node1, True)
    node4 = InternalNode(node1, True)
    assert len(node1.children) == 2
    assert node1.children[0] == node3
    assert node1.children[1] == node4


def test_notationtree1():
    n1 = m21.note.Note("E--5")
    n1.duration.quarterLength = 3
    n2 = m21.note.Note("D4")
    root = Root()
    node1 = InternalNode(root, True)
    node3 = LeafNode(node1, [gn2label(gn) for gn in [n1]])
    node4 = LeafNode(node1, [gn2label(gn) for gn in [n2]])
    nt1 = NotationTree(root, tree_type="beaming")
    assert nt1.get_leaf_nodes() == [node3, node4]
    assert nt1.get_nodes(local_root=node1) == [node1, node3, node4]
    assert nt1.get_nodes() == [root, node1, node3, node4]


def test_ntfromm21():
    score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
    measures = score.parts[0].getElementsByClass("Measure")
    # measure 0
    gns_m0 = measures[0].getElementsByClass("GeneralNote")
    label_gns_m0 = [gn2label(gn) for gn in gns_m0]
    expected_label_gns_m0 = [([{"npp": "G4", "alt": None, "tie": False}], 1, 0, False)]
    nt = ntfromm21(gns_m0, "BT")
    assert len(nt.get_nodes()) == 2
    assert len(nt.get_leaf_nodes()) == 1


######THings to do: every leaf accept only one general note. Grace notes are saved as different nodes!!
# Need to reformat many parts of the code
