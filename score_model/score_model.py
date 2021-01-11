import copy
import music21 as m21

from pathlib import Path

import score_model.m21utils as m21u


class ScoreModel:
    """Class that represent a score
    """

    def __init__(self, musicxml_path, auto_format=True, produce_trees=False):
        """Initialize the ScoreModel from a music21 score object

        Args:
            musicxml_path: the path of the music_xml to import
            auto_format (bool, optional): Auto format the score with the hierarchy score, parts, measures, voices. Defaults to True.
            produce_trees (bool, optional): Produce the BT and TT for each measure. Defaults to False.
        """
        self.m21_score = m21.converter.parse(str(Path(musicxml_path)))
        m21u.reconstruct(self.m21_score)
        print("created")

    def get_voices(self):
        voices = []
        for ip, p in enumerate(self.m21_score.parts):
            voices.append([])
            for im, m in enumerate(p.getElementsByClass(m21.stream.Measure)):
                # consider only the first voice (TO UPDATE)
                voice = m.getElementsByClass(m21.stream.Voice)[0]
                notes = voice.getElementsByClass("GeneralNote")
                voices[ip].extend(notes)

        return [m21u.m21_2_timeline(v) for v in voices]

