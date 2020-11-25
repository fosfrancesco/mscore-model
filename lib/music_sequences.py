from numbers import Number
import numpy as np
from fractions import Fraction
from lib.bar_trees import *
import numbers
import functools

CONTINUATION_SYMBOL = 0


class Event:
    def __init__(self, timestamp, musical_artifact):
        self.timestamp = timestamp
        self.musical_artifact = musical_artifact

    def __add__(self, number: numbers.Number):
        return Event(self.timestamp + number, self.musical_artifact)

    def __sub__(self, number: numbers.Number):
        return Event(self.timestamp - number, self.musical_artifact)

    def __mul__(self, number: numbers.Number):
        return Event(self.timestamp * number, self.musical_artifact)

    def __truediv__(self, number: numbers.Number):
        return Event(self.timestamp / number, self.musical_artifact)

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __eq__(self, other):
        return (self.timestamp, self.musical_artifact) == other

    def __str__(self):
        return str((self.timestamp, self.musical_artifact))

    def __repr__(self):
        return str((self.timestamp, self.musical_artifact))


class Timeline:
    def __init__(
        self, events, start=0, end=1, auto_sort=False,
    ):
        if auto_sort:  # sort if requested
            events = sorted(events)
        if (
            len(events) == 0 or events[0].timestamp != start
        ):  # if the first event does not happen on start
            # add a continuation at the beginning
            events = np.concatenate(([Event(start, CONTINUATION_SYMBOL)], events))
        self.events = np.array(events)
        self.start = start
        self.end = end

    def get_timestamps(self):
        return [e.timestamp for e in self.events]

    def get_musical_artifacts(self):
        return [e.musical_artifact for e in self.events]

    def __len__(self):
        return len(self.events)

    def __repr__(self):
        return "Tim{},[{},{}[".format(self.events, self.start, self.end)

    def __eq__(self, other):
        if not isinstance(other, Timeline):
            return False
        else:
            return (
                np.array_equal(self.events, other.events)
                and self.start == other.start
                and self.end == other.end
            )

    def split(self, k: int, normalize: bool = False):
        # compute the split points
        split_points = [
            Fraction(i, k) * Fraction((self.end - self.start)) + Fraction(self.start)
            for i in range(0, k + 1)
        ]
        # compute the indices where we need to split
        split_indices = [
            np.searchsorted(self.get_timestamps(), s) for s in split_points
        ]
        # split the events according to those indices (and normalize if required)
        return [
            Timeline(
                (self.events[ind[0] : ind[1]] - split_points[i]) * k + self.start,
                start=self.start,
                end=self.end,
            )
            if normalize
            else Timeline(
                self.events[ind[0] : ind[1]],
                start=split_points[i],
                end=split_points[i + 1],
            )
            for i, ind in enumerate(zip(split_indices[:-1], split_indices[1:]))
        ]

    def shift_and_rescale(self, new_start=0, new_end=1):
        return Timeline(
            (self.events - self.start)
            * Fraction(new_end - new_start, self.end - self.start)
            + new_start,
            start=new_start,
            end=new_end,
        )


def split_content(seq, k: int, interval=(0, 1)):
    """Split the content of a sorted array in equal intervals.

    For an interval (a,b) it will split at positions [Fraction(i, k) * a + b) for i in range(1, k)].
    For example for the interval (0,2) with k=4, it will split at 0.5,1,1.5.
    WARNING: the sequence should contains Fraction with limit_denominator to avoid rounding problems.
    Also problematic fractions like 0.1 could create problems

    Args:
        seq (list): the input list of numbers
        k (int): the number of intervals

    Returns:
        list: A list of intervals
    """
    # compute the indices where we need to split
    split_indices = [
        np.searchsorted(
            seq,
            Fraction(i, k) * Fraction((interval[1] - interval[0]))
            + Fraction(interval[0]),
        )
        for i in range(1, k)
    ]
    # split according to the indices
    return np.split(seq, split_indices)


def musical_split(seq, k: int):
    """Split a sequence of musical events in the interval [0,1[ in subsequences and rescale them.

    This function add the beginning of the interval. 
    For example music splitting the sequence [0,0.25,0.75] in 2 parts generates two arrays [0,0.5], [0,0.5]

    Args:
        seq (list): the input list of temporal postion of musical events
        k (int): the number of intervals
    """
    borders = [Fraction(i, k) for i in range(0, k + 1)]
    return [
        (np.concatenate(([b], o)) - b) * Fraction(k)
        if (o.size == 0 or o[0] != b)
        else (o - b) * Fraction(k)
        for b, o in zip(borders[:-1], split_content(seq, k, (0, 1)))
    ]


def timestamps2rhythm_tree(seq: np.array, depth: int, subtree_parent: Node):
    if depth > 6:  # stop recursion because maximum depth is reached
        pass
    elif seq.size == 1:  # stop recursion (size can never be 0 from musical_split)
        LeafNode(subtree_parent, [list(seq)])
    else:
        recursive_choices = (
            []
        )  # list of subsubtrees parents corresponding to differen division values
        for k in [2, 3, 5, 7]:
            subsubtree_parent = InternalNode(None, "")
            for subseq in musical_split(seq, k):
                timestamps2rhythm_tree(subseq, depth + 1, subsubtree_parent)
            recursive_choices.append(subsubtree_parent)
        # find the best division value (if it exists), i.e. the one generating the tree with minimum number of leaves
        min_leaves_subtree_index = np.argmin(
            [n.subtree_leaves() for n in recursive_choices]
        )
        # connect this to the subtree parent
        subtree_parent.add_child(recursive_choices[min_leaves_subtree_index])
        recursive_choices[min_leaves_subtree_index].parent = subtree_parent


def timeline2rt(tim: Timeline, allowed_divisions=[2, 3]):
    tim = tim.shift_and_rescale(new_start=0, new_end=1)  # rescale the input timeline
    root = Root()
    __timeline2rt(tim, 0, root, allowed_divisions)
    if (
        isinstance(root.children[0], InternalNode)
        and len(root.children[0].children) == 0
    ):
        print("Multiple minimum leaves tree for the input timeline")
        return None
    else:
        return RhythmTree(root)


def __timeline2rt(
    tim: Timeline, depth: int, subtree_parent: Node, allowed_divisions: list
):
    """Recursive function that create a Rhythm Tree from a timeline, called from timeline2rt.

    It build the tree attaching at each step the best subtree to subtree_parent.
    It work bottom-up making the choice for the tree with minimum number of leaves at each step.

    Args:
        tim (Timeline): the input timeline
        depth (int): the depth of the recursion (used to stop if it exeed a maximum recursion)
        subtree_parent (Node): the parent node for the current step
        allowed_divisions (list): the list of divisions explored by the algorithm
    """
    if depth > 6:  # stop recursion because maximum depth is reached
        InternalNode(
            subtree_parent, ""
        )  # we put an internal node without leaves that will be pruned later
    elif len(tim.events) == 1:  # stop recursion (size can never be 0 in a Timeline)
        LeafNode(subtree_parent, [[tim.events[0].musical_artifact]])
    else:
        recursive_choices = (
            []
        )  # list of subsubtrees parents corresponding to differen division values
        for k in allowed_divisions:
            subsubtree_parent = InternalNode(None, "")
            for subtim in tim.split(k, normalize=True):
                __timeline2rt(subtim, depth + 1, subsubtree_parent, allowed_divisions)
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
            if len(min_indices) > 1:  # if min is not unique we exit from the recursion
                InternalNode(
                    subtree_parent, ""
                )  # we put an internal node without leaves that will be pruned later
            else:  # connect this to the subtree parent
                subtree_parent.add_child(recursive_choices[min_indices[0]])
                recursive_choices[min_indices[0]].parent = subtree_parent
