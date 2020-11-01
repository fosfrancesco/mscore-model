#%%
import music21 as m21
from pathlib import Path
from lib.m21utils import *
from lib.NotationTree import *

score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
measures = score.parts[0].getElementsByClass("Measure")
# measure 0
gns_m0 = measures[0].getElementsByClass("GeneralNote")
label_gns_m0 = [gn2label(gn) for gn in gns_m0]
expected_label_gns_m0 = [([{"npp": "G4", "alt": None, "tie": False}], 1, 0, False)]
nt = ntfromm21(gns_m0, "BT")
nt.show()

# %%
