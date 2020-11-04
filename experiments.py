#%%
import music21 as m21
from pathlib import Path
from lib.m21utils import *
from lib.NotationTree import *
import importlib


score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
measures = score.parts[0].getElementsByClass("Measure")
# measure 1
gns_m1 = measures[1].getElementsByClass("GeneralNote")
nt = ntfromm21(gns_m1, "beamings")

print(m21_2_seq_struct(gns_m1, "beamings")[0])
print(m21_2_seq_struct(gns_m1, "beamings")[1])
leaves = nt.get_leaf_nodes()
print([nt.get_depth(leaf) for leaf in leaves])
leaves_connection = [nt.get_lca(n1, n2) for n1, n2 in window(leaves)]
print([nt.get_depth(n) for n in leaves_connection])

print("_________________")
print(nt2seq_structure(nt))


# %%
a = []
a.append("ciao")
a

# %%
