import music21 as m21
import numpy as np
from pathlib import Path
from fractions import Fraction

from score_model.bar_trees import (
    Root,
    LeafNode,
    InternalNode,
    timeline2rt,
    NotationTree,
    RhythmTree,
    simplify_label,
)
from score_model.m21utils import gn2label
from score_model.music_sequences import Event, Timeline


def test_notenode1():
    n1 = m21.note.Note("E--5")
    n1.duration.quarterLength = 3
    n2 = m21.note.Note("D4")
    n_grace = n2.getGrace()
    root = Root()
    node1 = LeafNode(root, [gn2label(gn) for gn in [n_grace, n1]])
    assert node1.label == [
        ([{"npp": "D4", "acc": None, "tie": False}], 4, 0, True),
        ([{"npp": "E5", "acc": -2, "tie": False}], 2, 1, False),
    ]
    assert str(node1) == str(
        [
            ([{"npp": "D4", "acc": None, "tie": False}], 4, 0, True),
            ([{"npp": "E5", "acc": -2, "tie": False}], 2, 1, False),
        ]
    )
    assert root.complete()
    assert node1.complete()


def test_internalnode1():
    root = Root()
    node1 = InternalNode(root, True)
    node3 = InternalNode(node1, True)
    node4 = InternalNode(node1, True)
    assert len(node1.children) == 2
    assert node1.children[0] == node3
    assert node1.children[1] == node4
    assert not node1.complete()


def test_notationtree1():
    n1 = m21.note.Note("E--5")
    n1.duration.quarterLength = 3
    n2 = m21.note.Note("D4")
    root = Root()
    node1 = InternalNode(root, "")
    node3 = LeafNode(node1, gn2label(n1))
    node4 = LeafNode(node1, gn2label(n2))
    nt1 = NotationTree(root, tree_type="beaming")
    assert nt1.get_leaf_nodes() == [node3, node4]
    assert nt1.get_nodes(local_root=node1) == [node1, node3, node4]
    assert nt1.get_nodes() == [root, node1, node3, node4]
    assert nt1.get_depth(root) == 0
    assert nt1.get_depth(node1) == 1
    assert nt1.get_depth(node3) == 2
    assert nt1.get_ancestors(root) == []
    assert nt1.get_ancestors(node4) == [node1, root]
    assert nt1.get_lca(node3, node4) == node1
    assert nt1.get_lca(node4, node3) == node1
    assert nt1.get_lca(root, node4) == root
    assert nt1.get_lca(node4, root) == root
    assert root.complete()


def test_rhythmtree1():
    root = Root()
    node0 = InternalNode(root, "")
    node1 = InternalNode(root, "")
    node2 = LeafNode(node0, 0)
    node3 = InternalNode(node1, "")
    node4 = InternalNode(node1, "")
    node5 = InternalNode(node1, "")
    node6 = LeafNode(node3, [[44], [45, 48, 50]])
    node7 = LeafNode(node4, [[55]])
    node8 = LeafNode(node5, [[55]])
    rt = RhythmTree(root)
    assert rt.node_duration(node0) == 0.5
    assert rt.node_duration(node1) == 0.5
    assert rt.node_duration(node2) == Fraction(1, 2)
    assert rt.node_duration(node6) == Fraction(1, 6)
    assert root.subtree_leaves() == 4
    assert node7.subtree_leaves() == 1
    assert np.array_equal(
        rt.get_leaves_timestamps(),
        [Fraction(0, 1), Fraction(1, 2), Fraction(2, 3), Fraction(5, 6)],
    )


def test_timeline2rt():
    tim1 = Timeline([Event(0, [88]), Event(1, [90])], start=0, end=3)
    rt1 = timeline2rt(tim1)
    assert list(rt1.get_leaves_timestamps()) == [0, Fraction(1, 3), Fraction(2, 3)]
    # test with grace notes
    tim2 = Timeline(
        [Event(0, [87]), Event(0, [88]), Event(1, [90, 94])], start=0, end=3
    )
    rt2 = timeline2rt(tim2)
    assert list(rt2.get_leaves_timestamps()) == [0, Fraction(1, 3), Fraction(2, 3)]
    assert rt2.get_timeline(0, 3) == tim2
    # test with multiple minimum leaves trees
    tim3 = Timeline([Event(Fraction(i, 3), [40]) for i in range(6)], start=0, end=2)
    rt3 = timeline2rt(tim3)
    assert rt3 is None
    # test with multiple minimum leaves trees and div preferences
    tim4 = Timeline([Event(Fraction(i, 3), [40]) for i in range(6)], start=0, end=2)
    rt4 = timeline2rt(tim4, max_depth=3, div_preferences=[3, 2, 2])
    assert len(rt4.get_leaf_nodes()[0].parent.children) == 2
    # test with multiple minimum leaves trees and div preferences2
    tim5 = Timeline([Event(Fraction(i, 3), [40]) for i in range(6)], start=0, end=2)
    rt5 = timeline2rt(tim5, max_depth=3, div_preferences=[2, 3, 3])
    assert len(rt5.get_leaf_nodes()[0].parent.children) == 3


def test_simplify_label1():
    n1 = m21.note.Note("E--5")
    n1.duration.quarterLength = 3
    assert simplify_label(gn2label(n1)) == "[E5bb]2*"


def test_simplify_label2():
    n1 = m21.note.Note("D4")
    n_grace = n1.getGrace()
    n2 = m21.note.Note("E#5")
    assert simplify_label(gn2label(n_grace)) == "[D4]4gn"
