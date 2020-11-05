#%%
import music21 as m21
from pathlib import Path
from lib.m21utils import *
from lib.NotationTree import *
import importlib

# m21.environment.set(
#     "musescoreDirectPNGPath",
#     "/mnt/c/Program Files (x86)/MuseScore 2//bin/MuseScore.exe",
# )
# m21.environment.set(
#     "musicxmlPath", "/mnt/c/Program Files (x86)/MuseScore 2//bin/MuseScore.exe"
# )

# us = m21.environment.UserSettings()
# # us.create()
# us["musescoreDirectPNGPath"] = "/usr/bin/musescore"
# us["musicxmlPath"] = "/usr/bin/musescore"

score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
measures = score.parts[0].getElementsByClass("Measure")
m = measures[4]

gns = m.getElementsByClass("GeneralNote")
bt = m21_2_notationtree(gns, "beamings")
tt = m21_2_notationtree(gns, "tuplets")

m21u.nt2general_notes(bt, tt)


# %%
