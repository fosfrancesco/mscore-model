#%%
import music21 as m21
from pathlib import Path
from score_model.m21utils import *
import score_model

score = score_model.ScoreModel("tests/test_musicxml/test_multipart.musicxml")
len(score.m21_score.parts)

#%%
m21s = m21.converter.parse("tests/test_musicxml/test_score1.musicxml")
m21s.show("text")

#%%
tim = score.get_voices()
print(tim)
#%%
m21.environment.set(
    "musescoreDirectPNGPath", "C:\\Program Files (x86)\\MuseScore 2\\bin\\MuseScore.exe"
)
m21.environment.set(
    "musicxmlPath", "C:\\Program Files (x86)\\MuseScore 2\\bin\\MuseScore.exe"
)

env = m21.environment.Environment()

# check the path
print("Environment settings:")
print("musicXML:  ", env["musicxmlPath"])
print("musescore: ", env["musescoreDirectPNGPath"])

#%%
files = [
    str(Path("tests/test_musicxml/101-Beethoven-bagatelle4op33.xml")),
]

for xmlfile in files:
    score = m21.converter.parse(str(Path(xmlfile)))
    add_nt_to_score(score)

# #%%
# get environment
env = m21.environment.Environment()

# check the path
print("Environment settings:")
print("musicXML:  ", env["musicxmlPath"])
print("musescore: ", env["musescoreDirectPNGPath"])

# set path if necessary
env["musicxmlPath"] = "path/to/your/musicXmlApplication"
env["musescoreDirectPNGPath"] = "path/to/your/museScore"


# # us = m21.environment.UserSettings()
# # # us.create()
# # us["musescoreDirectPNGPath"] = "C:/Program Files (x86)/MuseScore 2/bin/MuseScore.exe"
# # us["musicxmlPath"] = "C:/Program Files (x86)/MuseScore 2/bin/MuseScore.exe"

# # us = m21.environment.UserSettings()
# # # us.create()
# # us["musescoreDirectPNGPath"] = "/usr/bin/musescore"
# # us["musicxmlPath"] = "/usr/bin/musescore"

# score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
# measures = score.parts[0].getElementsByClass("Measure")
# m = measures[3]

# gns = m.getElementsByClass("GeneralNote")
# bt = m21_2_notationtree(gns, "beamings")
# tt = m21_2_notationtree(gns, "tuplets")

# out_gns = nt2general_notes(bt, tt)

# print(m21_2_seq_struct(gns, "tuplets"))
# print(m21_2_seq_struct(out_gns, "tuplets"))


# for n1, n2 in zip(gns, out_gns):
#     print(gn2label(n1))
#     print(gn2label(n2))
#     print("***")
#     print(get_beams(n1), get_beams(n2))
#     print(get_tuplets(n1), get_tuplets(n2))
#     print("____________")

# s = m21.stream.Stream()
# for n in nt2general_notes(bt, tt):
#     s.append(n)

# # s.show()


# # %%
# # s[0][0].tie

# # %%
# score = m21.converter.parse(str(Path("tests/test_musicxml/test_score1.musicxml")))
# score.parts[0].getElementsByClass(m21.stream.Stream)[0].getElementsByClass(
#     m21.stream.Voice
# )


# # %%
# score = m21.converter.parse(str(Path("tests/test_musicxml/test_score2.musicxml")))
# reconstruct(score)
# expected_num_voices = [2, 1, 2, 1]
# for i, measure in enumerate(score.parts[0].getElementsByClass(m21.stream.Measure)):
#     print(len(measure.getElementsByClass(m21.stream.Voice)))
# # %%
# score = m21.converter.parse(str(Path("tests/test_musicxml/test_score2.musicxml")))
# # reconstruct(score)
# # score.parts[0].getElementsByClass(m21.stream.Measure)[2].show("text")
# score.show()
# # %%
# reconstruct(score)
# score.show()

# # %%
# score.show()

# %%
from score_model.server_communication import send_to_qparse
from score_model.music_sequences import Timeline, MusicalContent

