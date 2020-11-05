#%%
import music21 as m21
from pathlib import Path
from lib.m21utils import *
from lib.NotationTree import *
import importlib

m21.environment.set(
    "musescoreDirectPNGPath",
    "/mnt/c/Program Files (x86)/MuseScore 2//bin/MuseScore.exe",
)
m21.environment.set(
    "musicxmlPath", "/mnt/c/Program Files (x86)/MuseScore 2//bin/MuseScore.exe"
)

# us = m21.environment.UserSettings()
# # us.create()
# us["musescoreDirectPNGPath"] = "/usr/bin/musescore"
# us["musicxmlPath"] = "/usr/bin/musescore"

score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
measures = score.parts[0].getElementsByClass("Measure")
for i, m in enumerate(measures):
    print("measure", i)
    gns = m.getElementsByClass("GeneralNote")
    bt = m21_2_notationtree(gns, "beamings")
    tt = m21_2_notationtree(gns, "tuplets")
    print(m21_2_seq_struct(gns, "beamings")[1])
    print(nt2seq_structure(bt)[1])
    # assert m21_2_seq_struct(gns, "tuplets")[1] == nt2seq_structure(tt)[1]

score = m21.corpus.parse("bach/bwv295")
score.show()

# %%
a = []
a.append("ciao")
a

# %%
