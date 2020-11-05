# from music21 import *
import lib.m21utils as m21u
from fractions import Fraction

# Digraph and the show() function are not useful for some application, so can be commented to reduce the dependencies
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

        if self.type != "root":
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
        size = 1
        for c in self.get_children():
            size += c.subtree_size()
        return size

    def has_children(self):
        if len(self.children) == 0:
            return False
        else:
            return True

    def get_subtree_nodes(self):
        return self._all_nodes(self, [])

    def atomic(self):
        return len(self.children) == 0

    def not_atomic(self):
        return len(self.children) != 0

    def unary(self):
        return len(self.children) == 1

    def not_unary(self):
        return len(self.children) != 1

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

    def to_string(self):
        return str(self.label)


class NotationTree:
    """The class for the Notation Tree.

    Two kinds of notation trees exist: beaming tree (BT) and tuplet tree (TT), 
    encoding in the tree structure respectively the beaming and the tuplet information in a voice in  a measure.
    The information about the notes are encoded in leaves and the same for the BT and the TT of a voice in a measure.
    """

    def __init__(self, root, tree_type=None, quality_check=True):
        """Initialize the notation tree.

        All the nodes must be already created and correctly linked to each other.
        This class just give functions on top of that structure.

        Args:
            root (Node): the tree root.
            tree_type (str, optional): either "beamings" or "tuplets". Defaults to None.
            quality_check (bool, optional): True if we want to check the format of the tree. Set it to false to improve speed. Defaults to True.

        Raises:
            TypeError: if the node structure linked to root is not valid.
        """
        self.root = root
        if quality_check:
            # perform some quality check to verify that the set of nodes are valid
            if not isinstance(self.root, Root):  # check if the root is a root node
                raise TypeError("Parameter root must be of type Root")
            # check if notes without childrens are leaves
            for node in self.get_nodes():
                if not node.has_children():
                    if not isinstance(node, LeafNode):
                        raise TypeError("Input subtree (rooted by root) without leaves")
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
        if not isinstance(other, NotationTree):
            return False
        else:
            return str(self) == str(other)

    # Comment to reduce the dependencies from graphviz
    def show(self, save=False, name=""):
        """Print a graphical version of the tree"""
        tree_repr = Digraph(comment="Notation Tree")
        tree_repr.node("1", "")  # the root
        self._recursive_tree_display(self.root, tree_repr, "11")
        if save:
            tree_repr.render("test-output/" + str(self.tree_type) + name, view=True)
        return tree_repr

    def _recursive_tree_display(self, node, _tree, name):
        """The recursive function called by show()."""
        for l in node.children:
            if l.type == "leaf":  # if it is a leaf
                _tree.node(name, m21u.simplify_label(l.label), shape="box")
                _tree.edge(name[:-1], name, constraint="true")
                name = name[:-1] + str(int(name[-1]) + 1)
            else:
                _tree.node(name, str(l.label))
                # _tree.node(name, str(l.get_duration()))
                _tree.edge(name[:-1], name, constraint="true")
                self._recursive_tree_display(l, _tree, name + "1")
                name = name[:-1] + str(int(name[-1]) + 1)

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


##########################################


# self.root = Root()
#         self.tree_type = tree_type
#         if notelist is not None:
#             if tree_type == "beams":
#                 self.beamings = m21u.get_enhance_beamings(
#                     self.note_list
#                 )  # beams and type (type for note shorter than quarter notes)
#                 # print(self.en_beam_list)
#                 ties_list = get_ties(self.note_list)
#                 # create a list of notes with ties and beaming information attached
#                 self.annot_notes = []
#                 # create a fake tuple info in order to assign names
#                 self.tuple_info = get_enhance_beamings(self.note_list)
#                 for i in range(len(self.tuple_info)):
#                     for ii in range(len(self.tuple_info[i])):
#                         self.tuple_info[i][ii] = ""
#                 for i, n in enumerate(self.note_list):
#                     self.annot_notes.append(
#                         AnnotatedNote(
#                             n,
#                             ties_list[i],
#                             self.en_beam_list[i],
#                             tuple_info=self.tuple_info[i],
#                         )
#                     )
#                 self._recursive_tree_generation(self.annot_notes, self.root, 0)
#             elif tree_type == "tuplets":
#                 self.tuplet_list = get_tuplets_type(
#                     self.note_list
#                 )  # corrected tuplets (with "start" and "continue")
#                 ties_list = get_ties(self.note_list)
#                 self.tuple_info = get_tuplets_info(self.note_list)
#                 # create a list of notes with ties and tuplets information attached
#                 self.annot_notes = []
#                 for i, n in enumerate(self.note_list):
#                     self.annot_notes.append(
#                         AnnotatedNote(
#                             n,
#                             ties_list[i],
#                             self.tuplet_list[i],
#                             tuple_info=self.tuple_info[i],
#                         )
#                     )
#                 self._recursive_tree_generation(self.annot_notes, self.root, 0)
#             else:
#                 raise TypeError("Invalid tree_type")


# class FullNoteTree:
#     def __init__(self, measure, bar_reference=None, mei_id=None):
#         self.beams_tree = NoteTree(measure=measure, tree_type="beams")
#         self.tuplets_tree = NoteTree(measure=measure, tree_type="tuplets")
#         self.en_beam_list = self.beams_tree.en_beam_list
#         self.tuplets_list = self.tuplets_tree.tuplet_list
#         self.bar_reference = bar_reference
#         self.mei_id = mei_id

#     def __eq__(self, other):
#         if not isinstance(other, FullNoteTree):
#             return False
#         else:
#             return (self.beams_tree == other.beams_tree) and (
#                 self.tuplets_tree == other.tuplets_tree
#             )

#     def subtree_size(self):
#         ######################to update with also the tuplet tree############
#         ######################################################################
#         return self.beams_tree.root.subtree_size()

#     # Comment to reduce dependencies (from graphviz)
#     def show(self, name=""):
#         self.beams_tree.show(name=name)
#         self.tuplets_tree.show(name=name)

#     def __repr__(self):
#         return str((str(self.beams_tree), str(self.tuplets_tree)))

#     def __str__(self):
#         return str((str(self.beams_tree), str(self.tuplets_tree)))


# class MonophonicScoreTrees:
#     def __init__(self, score):
#         """
#         Take a monophonic music21 score and store it a sequence of Full Trees
#         Arguments:
#             score {[music21 score]} a monofonic music21 score
#         Raises:
#             Exception -- [if there is more than 1 part]
#             Exception -- [if the part has more than 1 voice]
#         """
#         self.measuresTrees = []  # contains a FullNoteTree for each measure
#         if len(score.parts) != 1:  # check that the score have just one part
#             raise Exception("The score have more than one part")
#         for measure_index, measure in enumerate(
#             score.parts[0].getElementsByClass("Measure")
#         ):
#             if (
#                 len(measure.voices) == 0
#             ):  # there is a single Voice ( == for the library there are no voices)
#                 self.measuresTrees.append(
#                     FullNoteTree(
#                         measure,
#                         bar_reference=measure_index,
#                         mei_id=[note.id for note in get_notes(measure)],
#                     )
#                 )
#             else:  # there are multiple voices (or an array with just one voice)
#                 if len(measure.voices) != 1:
#                     raise Exception("The part 1 has more than one voice")
#                 for voice in measure.voices:
#                     self.measuresTrees.append(
#                         FullNoteTree(
#                             voice,
#                             bar_reference=measure_index,
#                             mei_id=[note.id for note in get_notes(voice)],
#                         )
#                     )

#     def __eq__(self, other):
#         if not isinstance(other, MonophonicScoreTrees):
#             return False
#         else:
#             if len(self.measuresTrees) != len(
#                 other.measuresTrees
#             ):  # chek if they have the same number of measures
#                 return False
#             for fnt in zip(
#                 self.measuresTrees, other.measuresTrees
#             ):  # check if FullNoteTree are the same for each bar
#                 if fnt[0] != fnt[1]:
#                     return False
#             return True


# class ScoreTrees:
#     def __init__(self, score):
#         """
#         Take a music21 score and store it a sequence of Full Trees
#         The hierarchy is "score -> parts ->measures -> voices -> notes"
#         Arguments:
#             score {[music21 score]} a music21 score
#         """
#         self.part_list = []  # contains a FullNoteTree for each measure
#         print("#parts = {}".format(len(score.parts)))
#         for part_index, part in enumerate(score.parts.stream()):
#             print(
#                 "#measure for part {} = {}".format(
#                     part_index, len(part.getElementsByClass("Measure"))
#                 )
#             )
#             tree_part = []  # tree part is a list of tree measures
#             for measure_index, measure in enumerate(part.getElementsByClass("Measure")):
#                 tree_measure = (
#                     []
#                 )  # measure is a list of voices (each represented by a FNT)
#                 if (
#                     len(measure.voices) == 0
#                 ):  # there is a single Voice ( == for the library there are no voices)
#                     print("Part {}, measure {}".format(part_index, measure_index))
#                     tree_measure.append(
#                         FullNoteTree(
#                             measure,
#                             bar_reference=measure_index,
#                             mei_id=[note.id for note in get_notes(measure)],
#                         )
#                     )
#                 else:  # there are multiple voices (or an array with just one voice)
#                     for voice in measure.voices:
#                         print("Part {}, measure {}".format(part_index, measure_index))
#                         tree_measure.append(
#                             FullNoteTree(
#                                 voice,
#                                 bar_reference=measure_index,
#                                 mei_id=[note.id for note in get_notes(voice)],
#                             )
#                         )
#                 tree_part.append(tree_measure)  # add the measures to the tree part
#             self.part_list.append(tree_part)  # add the complete part to part_list

#     # def __eq__(self,other):
#     #     if not isinstance(other, MonophonicScoreTrees):
#     #         return False
#     #     else:
#     #         if len(self.measuresTrees)!= len(other.measuresTrees): #check if they have the same number of measures
#     #             return False
#     #         for fnt in zip (self.measuresTrees,other.measuresTrees): #check if FullNoteTree are the same for each bar
#     #             if fnt[0] != fnt[1]:
#     #                 return False
#     #         return True


# class ScoreTrees_single_voice:
#     def __init__(self, score):
#         """
#         Take a music21 score and store it a sequence of Full Trees
#         The hierarchy is "score -> parts ->measures -> voices -> notes"
#         Arguments:
#             score {[music21 score]} a music21 score
#         """
#         self.part_list = []  # contains a FullNoteTree for each measure
#         print("#parts = {}".format(len(score.parts)))
#         for part_index, part in enumerate(score.parts.stream()):
#             print(
#                 "#measure for part {} = {}".format(
#                     part_index, len(part.getElementsByClass("Measure"))
#                 )
#             )
#             tree_part = (
#                 []
#             )  # tree part is a list of single voices measures (each represented by a FNT)
#             for measure_index, measure in enumerate(part.getElementsByClass("Measure")):
#                 if (
#                     len(measure.voices) == 0
#                 ):  # there is a single Voice ( == for the library there are no voices)
#                     print("Part {}, measure {}".format(part_index, measure_index))
#                     tree_part.append(
#                         FullNoteTree(
#                             measure,
#                             bar_reference=measure_index,
#                             mei_id=[note.id for note in get_notes(measure)],
#                         )
#                     )
#                 else:  # there are multiple voices (or an array with just one voice)
#                     for voice in measure.voices[0:1]:
#                         print("Part {}, measure {}".format(part_index, measure_index))
#                         tree_part.append(
#                             FullNoteTree(
#                                 voice,
#                                 bar_reference=measure_index,
#                                 mei_id=[note.id for note in get_notes(voice)],
#                             )
#                         )
#             self.part_list.append(tree_part)  # add the complete part to part_list

