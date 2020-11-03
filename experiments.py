#%%
import music21 as m21
from pathlib import Path
from lib.m21utils import *
from lib.NotationTree import *
import importlib


# %%
n1 = m21.note.Note("E--5")
n1.duration.quarterLength = 3
n2 = m21.note.Note("D4")
root = Root()
node1 = InternalNode(root, True)
node3 = LeafNode(node1, gn2label(n1))
node4 = LeafNode(node1, gn2label(n2))
nt1 = NotationTree(root, tree_type="beaming")

nt1.get_lca(root, node4)

# %%
