# %%
import numpy as np
from fractions import Fraction
from lib.music_sequences import *
from pathlib import Path
import music21 as m21
import time
import lib.m21utils as m21u


score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
measures = score.parts[0].getElementsByClass("Measure")
gns_m = measures[6].getElementsByClass("GeneralNote")
tim = Timeline([Event(gn.offset, gn.pitch.midi) for gn in gns_m], start=0, end=4)


rt = timeline2rt(tim)
rt.show()


# %%

bt = m21u.m21_2_notationtree(gns_m, "beamings")
bt.show()


# %%
from fractions import Fraction

score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
measures = score.parts[0].getElementsByClass("Measure")
gns_m = measures[4].getElementsByClass("GeneralNote")
m21u.m21_2_timeline(gns_m)

# %%
