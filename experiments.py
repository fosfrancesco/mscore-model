# %%
import numpy as np
from fractions import Fraction
from lib.music_sequences import *
from lib.bar_trees import *

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
rt.show()
rt.get_leaves_timestamps()
# %%
Fraction(0.1).limit_denominator()

# %%
import numpy as np

a = np.array([2, 3, 1])
b = np.array(["a", "b", "c"])

z = zip(b, a)

list(z)

# %%
