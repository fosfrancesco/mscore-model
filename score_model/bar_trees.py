from .music_sequences import Event, Timeline
from .constant import REST_SYMBOL, CONTINUATION_SYMBOL

from fractions import Fraction
from pathlib import Path
import numpy as np
from graphviz import Digraph


class Node:
    """The generic Tree node class."""

    def __init__(self, parent, type, label=None):
        """Initialize a node.

        This node is automatically added to the children list of the parent node.

        Args:
            parent (Node): the node parent
            type (string): a string that can be "root", "internal", "leaf"
            label ([object], optional): Some information contained in the node. Defaults to None.
        """
        self.type = type
        self.children = []  # each child is a Node
        self.parent = parent
        self.label = label
        self.duration = None  # we initialize that when the tree is builded and complete

        if self.parent is not None:
            parent.add_child(
                self
            )  # add a child in the parent Node if the parent is not the root

    def add_child(self, child):
        """Add a children to the node. Not really useful in standard utilisation, as a new node is added to the children list when it is created."""
        self.children.append(child)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def to_string(self):
        """Return the string representation of the subtree under the Node. This class is overridden in LeafNode to make the recursion stop."""
        out_string = str(self.label) + "("
        for c in self.children:
            out_string = out_string + c.to_string() + ","
        out_string = out_string[0:-1]  # remove the last comma
        out_string += ")"  # close the grouping
        return out_string

    def subtree_size(self):
        """Return the number of nodes in the subtree under the node (counting also the node itself).This class is overridden in LeafNode to make the recursion stop."""
        return 1 + sum([c.subtree_leaves() for c in self.children])

    def subtree_leaves(self):
        """Return the number of leaves in the subtree under the node.This class is overridden in LeafNode to make the recursion stop."""
        return sum([c.subtree_leaves() for c in self.children])

    def has_children(self):
        if len(self.children) == 0:
            return False
        else:
            return True

    def atomic(self):
        return len(self.children) == 0

    def not_atomic(self):
        return len(self.children) != 0

    def unary(self):
        return len(self.children) == 1

    def not_unary(self):
        return len(self.children) != 1

    def complete(self):
        """Return true if all the subtree under the node either have children or are LeafNodes"""
        if self.type == "leaf":
            return True
        elif len(self.children) == 0:
            return False
        else:
            return all([c.complete() for c in self.children])

    def __eq__(self, other):
        return self.to_string() == other.to_string()


class Root(Node):
    """The class for the Root node (e.g. without parent), extending Node."""

    def __init__(self):
        Node.__init__(self, None, "root")

    def get_parent(self):
        raise TypeError("Root nodes have no parent")


class InternalNode(Node):
    """The class for the Internal node, extending Node."""

    def __init__(self, parent, label):
        Node.__init__(self, parent, "internal", label)


class LeafNode(Node):
    """The class for the Leaf node, extending Node."""

    def __init__(self, parent, label):
        Node.__init__(self, parent, "leaf", label)

    def subtree_size(self):
        return 1

    def subtree_leaves(self):
        return 1

    def to_string(self):
        return str(self.label)


class Tree:
    """The generic class for trees"""

    def __init__(self, root):
        self.root = root

    def get_nodes(self, local_root=None):
        """Return a list with all nodes in the tree."""

        def _all_nodes(node, children_list):  # the recursive function
            children_list.append(node)  # add the current node
            for c in node.children:
                _all_nodes(c, children_list)
            return children_list

        if local_root is None:
            local_root = self.root
        return _all_nodes(local_root, [])

    def get_leaf_nodes(self, local_root=None):
        """Return a list with all Leaf Nodes in the tree."""
        if local_root is None:
            local_root = self.root
        return [
            n for n in self.get_nodes(local_root=local_root) if isinstance(n, LeafNode)
        ]

    def get_depth(self, node):
        """Return the depth of a node in the tree."""
        if node.type == "root":
            return 0
        else:  # iterative call
            if not isinstance(node.parent, Node):  # and structure check
                raise Exception("The parent of node", self, "has to be a Node")
            else:
                return 1 + self.get_depth(node.parent)

    def get_ancestors(self, node):
        """Get a list of all the ancestors in the tree of a node."""
        return self._get_ancestors(node)[1:]  # remove the node itself

    def _get_ancestors(self, node):
        """Recursive function called by get_ancestors."""
        if node.type == "root":
            return [node]
        else:  # recursive call
            if not isinstance(node.parent, Node):  # and structure check
                raise Exception("The parent of node", self, "has to be a Node")
            else:
                out = [node]
                out.extend(self._get_ancestors(node.parent))
                return out

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        else:
            return str(self) == str(other)

    def get_lca(self, node1, node2):
        """Get the lower common ancestor (lca) of two input nodes.

        Args:
            node1 (Node): the first node to consider.
            node2 (Node): the second node to consider.

        Returns:
            Node: the lca of the input nodes.

        """
        if (node1 not in self.get_nodes()) or (node2 not in self.get_nodes()):
            raise Exception("Input nodes should belong to the Notation Tree")
        if node1 is node2:
            raise Exception("The two inputs must be distinct nodes")

        def _get_lca(anc_list, node):
            if id(node) in [id(n) for n in anc_list]:
                return node
            else:
                return _get_lca(anc_list, node.parent)

        node1_anc = self.get_ancestors(node1)
        node1_anc.append(node1)  # in node 1 is directly an ancestor of node2
        return _get_lca(node1_anc, node2)

    def to_string(self):
        return self.root.to_string()

    def __repr__(self):
        return self.root.to_string()

    def __str__(self):
        return self.root.to_string()

    # Comment to reduce the dependencies from graphviz
    def show(self, save=False, name="tree", simplify_label=lambda x: str(x)):
        """Print a graphical version of the tree.

        Args:
            save (bool, optional): save the image as a file. Defaults to False.
            name (str, optional): the file name. Defaults to "tree".
            simplify_label (function, optional): a function to simplify the tree labels for a clear visualization. Defaults is a function that does nothing.

        Returns:
            Digraph: the digraph object
        """
        tree_repr = Digraph(comment="Tree")
        tree_repr.node("1", "")  # the root
        self._recursive_tree_display(self.root, tree_repr, "11", simplify_label)
        if save:
            tree_repr.render(str(Path("test-output", name)), view=True)
        return tree_repr

    def _recursive_tree_display(self, node, _tree, name, simplify_label):
        """The recursive function called by show()."""
        for l in node.children:
            if l.type == "leaf":  # if it is a leaf
                _tree.node(name, simplify_label(l.label), shape="box")
                _tree.edge(name[:-1], name, constraint="true")
                name = name[:-1] + str(int(name[-1]) + 1)
            else:
                _tree.node(name, str(l.label))
                # _tree.node(name, str(l.get_duration()))
                _tree.edge(name[:-1], name, constraint="true")
                self._recursive_tree_display(l, _tree, name + "1", simplify_label)
                name = name[:-1] + str(int(name[-1]) + 1)


class NotationTree(Tree):
    """The class for the Notation Tree.

    Two kinds of notation trees exist: beaming tree (BT) and tuplet tree (TT), 
    encoding in the tree structure respectively the beaming and the tuplet information in a voice in  a measure.
    The information about the notes are encoded in leaves and the same for the BT and the TT of a voice in a measure.

    This class just provide functions on top of the Node structure.
    """

    def __init__(self, root, tree_type=None, quality_check=True):
        """Initialize the notation tree.

        All the nodes must be already created and correctly linked to each other.

        Args:
            root (Root): the tree root.
            tree_type (str, optional): either "beamings" or "tuplets". Defaults to None.
            quality_check (bool, optional): True if we want to check the format of the tree. Set it to false to improve speed. Defaults to True.

        Raises:
            TypeError: if the node structure linked to root is not valid.
        """
        Tree.__init__(self, root)
        self.tree_type = tree_type
        if quality_check:
            # perform some quality check to verify that the set of nodes are valid
            if not isinstance(self.root, Root):  # check if the root is a root node
                raise TypeError("Parameter root must be of type Root")
            # check if notes without childrens are leaves
            for node in self.get_nodes():
                if not node.has_children():
                    if not isinstance(node, LeafNode):
                        raise TypeError("There is an internal node without leaves")
            # check if leaves label is correctly formatted
            for node in self.get_leaf_nodes():
                if not isinstance(node.label, tuple):
                    raise TypeError("Leaf label" + str(node) + "should be a tuple")
                if len(node.label) != 4:
                    raise TypeError(
                        "Leaf label" + str(node) + "not correctly formatted"
                    )
                if not node.label[0] == "R":
                    keys = ["npp", "acc", "tie"]
                    for k in keys:
                        for pitch in node.label[0]:
                            if k not in pitch.keys():
                                raise TypeError(
                                    "Pitches in leaf label"
                                    + str(node)
                                    + "not correctly formatted"
                                )

    def show(self, save=False, name="tree"):
        tree_repr = Tree.show(
            self, save=False, name="tree", simplify_label=simplify_label
        )
        return tree_repr


class RhythmTree(Tree):
    """The class for Rhythm Trees. 
    
    Each node encode a specific duration that is divided equally between his children.
    Each LeafNode has a label that contains a list of general notes.
    Each general note is a list of pitches expressed as MIDI numbers.

    This class give functions on top of the Node structure.
    """

    def __init__(self, root, quality_check=True):
        """Initialize the Rhythm Tree.

        All the nodes must be already created and correctly linked to each other.
        

        Args:
            root (Root): the root node
            quality_check (bool, optional): True if we want to check the format of the tree. Set it to false to improve speed. Defaults to True.

        Raises:
            TypeError: if the Node structure under "root" is not valid for a Rhythm Tree.
        """
        Tree.__init__(self, root)
        if quality_check:
            # perform some quality check to verify that the set of nodes are valid
            if not isinstance(self.root, Root):  # check if the root is a root node
                raise TypeError("Parameter root must be of type Root")
            # check if notes without childrens are leaves
            for node in self.get_nodes():
                if not node.has_children():
                    if not isinstance(node, LeafNode):
                        raise TypeError("There is an internal node without leaves")
            # check if leaves label is correctly formatted
            for node in self.get_leaf_nodes():
                if node.label == 0:  # 0 represent a continuation
                    pass
                elif not isinstance(node.label, list):
                    raise TypeError(
                        "Each general note in leaf label"
                        + str(node)
                        + "should be a list of general notes."
                    )
                else:
                    for gn in node.label:
                        if gn == CONTINUATION_SYMBOL or gn == REST_SYMBOL:
                            pass  # a continuation symbol cannot be in a chord
                        elif not isinstance(gn, list):
                            raise TypeError(
                                "Leaf label"
                                + str(node)
                                + "should be a list of pitches."
                            )
                        else:
                            for pitch in gn:
                                if not isinstance(pitch, (int, np.integer)):
                                    raise TypeError(
                                        "Each pitch in each general note in leaf label"
                                        + str(node)
                                        + "should be an integer expressing the MIDI note number or 0 for a continuation."
                                    )

    def node_duration(self, node):
        duration = Fraction(1)
        for a in self.get_ancestors(node):
            duration = duration / len(a.children)
        return duration

    def get_leaves_timestamps(self, node=None):
        if node is None:
            node = self.root
        if isinstance(node, LeafNode):  # stop recursion
            return np.array([Fraction(0, 1)])
        else:  # recursive call: take the children results, shrink and shift it
            return np.concatenate(
                [
                    self.get_leaves_timestamps(node=c) / len(node.children)
                    + Fraction(i) / len(node.children)
                    for i, c in enumerate(node.children)
                ]
            )

    def get_timeline(self, start=0, end=1):
        leaves_timestamps = self.get_leaves_timestamps()
        leaves_labels = [node.label for node in self.get_leaf_nodes()]
        events = [
            Event(t, pitches)
            for label, t in zip(leaves_labels, leaves_timestamps)
            for pitches in label
            if pitches != CONTINUATION_SYMBOL
        ]
        timeline = Timeline(events, start=0, end=1)
        return timeline.shift_and_rescale(start, end)


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


def timeline2rt(
    tim: Timeline, allowed_divisions=[2, 3], max_depth=7, div_preferences=None
):
    """Generate a Rhythm Tree from a timeline.

    Args:
        tim (Timeline): the input timeline.
        allowed_divisions (list, optional): division to consider. Defaults to [2, 3].
        max_depth (int, optional): maximum depth to consider. Defaults to 7.
        div_preferences ([type], optional): different depth may have different preferred div values. Defaults to None.

    Returns:
        RhythmTree: the rhythm tree.
    """
    tim = tim.shift_and_rescale(new_start=0, new_end=1)  # rescale the input timeline
    root = Root()
    __timeline2rt(tim, 0, root, allowed_divisions, max_depth, div_preferences)
    if (
        isinstance(root.children[0], InternalNode)
        and len(root.children[0].children) == 0
    ):
        print("Multiple minimum leaves tree for the input timeline")
        return None
    else:
        return RhythmTree(root)


def __timeline2rt(
    tim: Timeline,
    depth: int,
    subtree_parent,
    allowed_divisions: list,
    max_depth: int,
    div_preferences,
):
    """Recursive function that create a Rhythm Tree from a timeline, called from timeline2rt.

    It build the tree attaching at each step the best subtree to subtree_parent.
    It work bottom-up making the choice for the tree with minimum number of leaves at each step.

    Args:
        tim (Timeline): the input timeline
        depth (int): the depth of the recursion (used to stop if it exeed a maximum recursion)
        subtree_parent (Node): the parent node for the current step
        allowed_divisions (list): the list of divisions values explored by the algorithm
        max_depth (int): the maximum depth of the recursion
        div_preferences (list | None): which division to accept at each level in case of multiple minima. If not None must have length [depth]
    """
    if depth >= max_depth:  # stop recursion because maximum depth is reached
        InternalNode(
            subtree_parent, ""
        )  # we put an internal node without leaves that will be pruned later
    elif all(
        [e.timestamp == 0 for e in tim.events]
    ):  # stop recursion if all events are on the left border of the timeline
        LeafNode(subtree_parent, [e.musical_artifact for e in tim.events])
    else:
        recursive_choices = (
            []
        )  # list of subsubtrees parents corresponding to differen division values
        for k in allowed_divisions:
            subsubtree_parent = InternalNode(None, "")
            for subtim in tim.split(k, normalize=True):
                __timeline2rt(
                    subtim,
                    depth + 1,
                    subsubtree_parent,
                    allowed_divisions,
                    max_depth,
                    div_preferences,
                )
            recursive_choices.append(subsubtree_parent)
        valid_choices = [n for n in recursive_choices if n.complete()]
        if len(valid_choices) == 0:  # no valid choice available
            InternalNode(
                subtree_parent, ""
            )  # we put an internal node without leaves that will be pruned later
        else:
            # find the best division value, i.e. the one generating the tree with minimum number of leaves
            min_leaves = min([n.subtree_leaves() for n in valid_choices])
            min_indices = [
                i
                for i, n in enumerate(valid_choices)
                if n.subtree_leaves() == min_leaves
            ]
            # connect this to the subtree parent
            if len(min_indices) > 1:  # if min is not unique
                if div_preferences is None:  # we stop the recursion
                    InternalNode(
                        subtree_parent, ""
                    )  # we put an internal node without leaves that will be pruned later
                else:  # we select one based on div_preferences
                    valid_choices = [
                        n for i, n in enumerate(valid_choices) if i in min_indices
                    ]
                    min_indices = [
                        i
                        for i, n in enumerate(valid_choices)
                        if len(n.children) == div_preferences[depth]
                    ]
                    # connect this to the subtree parent
                    subtree_parent.add_child(valid_choices[min_indices[0]])
                    valid_choices[min_indices[0]].parent = subtree_parent
            else:  # connect this to the subtree parent
                subtree_parent.add_child(valid_choices[min_indices[0]])
                valid_choices[min_indices[0]].parent = subtree_parent
