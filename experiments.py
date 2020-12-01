#%%
import music21 as m21
from pathlib import Path
from lib.m21utils import *
from lib.notation_tree import *
import importlib

# get environment
env = m21.environment.Environment()

# check the path
print("Environment settings:")
print("musicXML:  ", env["musicxmlPath"])
print("musescore: ", env["musescoreDirectPNGPath"])

# set path if necessary
# env['musicxmlPath'] = 'path/to/your/musicXmlApplication'
# env['musescoreDirectPNGPath'] = 'path/to/your/museScore'

# m21.environment.set(
#     "musescoreDirectPNGPath",
#     "C:/Program Files (x86)/MuseScore 2/bin/MuseScore.exe"
# )
# m21.environment.set(
#     "musicxmlPath", "C:/Program Files (x86)/MuseScore 2/bin/MuseScore.exe"
# )

# us = m21.environment.UserSettings()
# # us.create()
# us["musescoreDirectPNGPath"] = "C:/Program Files (x86)/MuseScore 2/bin/MuseScore.exe"
# us["musicxmlPath"] = "C:/Program Files (x86)/MuseScore 2/bin/MuseScore.exe"

# us = m21.environment.UserSettings()
# # us.create()
# us["musescoreDirectPNGPath"] = "/usr/bin/musescore"
# us["musicxmlPath"] = "/usr/bin/musescore"

score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
measures = score.parts[0].getElementsByClass("Measure")
m = measures[3]

gns = m.getElementsByClass("GeneralNote")
bt = m21_2_notationtree(gns, "beamings")
tt = m21_2_notationtree(gns, "tuplets")

out_gns = nt2general_notes(bt, tt)

print(m21_2_seq_struct(gns, "tuplets"))
print(m21_2_seq_struct(out_gns, "tuplets"))


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

#s.show()


# %%
#s[0][0].tie

# %%
