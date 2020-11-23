# %%
import numpy as np
from fractions import Fraction
from lib.music_sequences import *
from pathlib import Path
import music21 as m21


score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
measures = score.parts[0].getElementsByClass("Measure")
# measure 3 (grace note)
gns_m = measures[3].getElementsByClass("GeneralNote")
tim = Timeline([Event(gn.offset, gn.pitch.midi) for gn in gns_m], start=0, end=4)
tim = tim.shift_and_rescale(new_start=0, new_end=1)

root = Root()
timeline2rt(tim, 0, root)

rt = RhythmTree(root)
rt.show()
# %%
a = np.array([3, 4, 5, 6])
[1, 2] + a[0:3]

