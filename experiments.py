#%%
import music21 as m21
from pathlib import Path
from lib.m21utils import *
from lib.notation_tree import *
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
m = measures[2]

gns = m.getElementsByClass("GeneralNote")
bt = m21_2_notationtree(gns, "beamings")
tt = m21_2_notationtree(gns, "tuplets")

out_gns = nt2general_notes(bt, tt)
for n1, n2 in zip(gns, out_gns):
    print(gn2label(n1))
    print(gn2label(n2))
    print("***")
    print(get_beams(n1), get_beams(n2))
    print(get_tuplets(n1), get_tuplets(n2))
    print("____________")

s = m21.stream.Stream()
for n in nt2general_notes(bt, tt):
    s.append(n)

s.show("text")


# %%
n = m21.note.Note("B5-")
print(n.nameWithOctave)
c = m21.chord.Chord(["A2", "B5-", "B6"])
c[n.nameWithOctave + ".tie"] = "start"


c["B-5.tie"] = "stop"

for no in c:
    print(no.tie)

# %%
n = m21.note.Note("B5-")
print(n.tie)
