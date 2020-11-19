import music21 as m21
import lib.m21utils as m21u
from pathlib import Path
from fractions import Fraction

from lib.bar_trees import *


def test_notenode1():
    n1 = m21.note.Note("E--5")
    n1.duration.quarterLength = 3
    n2 = m21.note.Note("D4")
    n_grace = n2.getGrace()
    root = Root()
    node1 = LeafNode(root, [m21u.gn2label(gn) for gn in [n_grace, n1]])
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
    node1 = InternalNode(root, "")
    node3 = LeafNode(node1, m21u.gn2label(n1))
    node4 = LeafNode(node1, m21u.gn2label(n2))
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

