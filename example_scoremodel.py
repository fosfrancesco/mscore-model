import music21 as m21
from lib.m21utils import m21_2_score_model
from pathlib import Path

#m21_score = m21.corpus.parse('bach/bwv66_6.xml')
m21_score = m21.converter.parse(str(Path("tests/test_musicxml/test_score2.musicxml")))

#m21_score.show('txt')

score_model = m21_2_score_model(m21_score)
score_model.print()