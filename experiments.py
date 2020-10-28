#%%
import music21 as m21
from pathlib import Path
from lib.m21utils import *

score = m21.converter.parse(str(Path("tests/test_musicxml/test_score3.musicxml")))
measures = score.parts[0].getElementsByClass("Measure")
# measure 1
gns_m1 = measures[0].getElementsByClass("GeneralNote")

for gn in gns_m1:
    print([t.type for t in gn.duration.tuplets])

# [t.type for t in gns_m1[1].duration.tuplets]

# %%
