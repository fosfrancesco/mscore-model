import numpy as np
from fractions import Fraction
from lib.bar_trees import *


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


def sequence_to_rhythm_tree(seq: np.array, depth: int, subtree_parent: Node):
    if depth > 10:  # stop recursion because maximum depth is reached
        pass
    elif seq.size == 1:  # stop recursion (size can never be 0 from musical_split)
        LeafNode(subtree_parent, [list(seq)])
    else:
        recursive_choices = (
            []
        )  # list of subsubtrees parents corresponding to differen division values
        for k in [2, 3]:
            subsubtree_parent = InternalNode(None, "")
            for subseq in musical_split(seq, k):
                sequence_to_rhythm_tree(subseq, depth + 1, subsubtree_parent)
            recursive_choices.append(subsubtree_parent)
        # find the best division value, i.e. the one generating the tree with minimum number of leaves
        min_leaves_subtree_index = np.argmin(
            [n.subtree_leaves() for n in recursive_choices]
        )
        # connect this to the subtree parent
        subtree_parent.add_child(recursive_choices[min_leaves_subtree_index])
        recursive_choices[min_leaves_subtree_index].parent = subtree_parent
