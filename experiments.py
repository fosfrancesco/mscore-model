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
gns = measures[3].getElementsByClass("GeneralNote")
rt = m21u.m21_2_rhythmtree(gns, div_preferences=[2, 2, 2, 2, 2, 2, 2])
rt.show()

# %%

tt = m21u.m21_2_notationtree(gns, "tuplets")
tt.show()


# %%
bt = m21u.m21_2_notationtree(gns, "beamings")
bt.show()
