# %%
import numpy as np
from fractions import Fraction
from lib.music_sequences import *
from pathlib import Path
import music21 as m21
import time


score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
measures = score.parts[0].getElementsByClass("Measure")
gns_m = measures[3].getElementsByClass("GeneralNote")
tim = Timeline([Event(gn.offset, gn.pitch.midi) for gn in gns_m], start=0, end=4)

rt = timeline2rt(tim)
rt.show()

# %%
