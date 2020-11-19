import music21 as m21
from lib.m21utils import *
import importlib
from pathlib import Path



m21_score = m21.corpus.parse('bach/bwv323.xml')
m21_score.show('txt')