import copy
from score_model.music_sequences import Timeline
import music21 as m21

from pathlib import Path

import score_model.m21utils as m21u


class ScoreModel:
    """Class that represent a score.
    """

    def __init__(
        self, musicxml_path: str, auto_format: bool = True, produce_trees: bool = False
    ):
        """Initialize the ScoreModel from a music21 score object.

        Args:
            musicxml_path: the path of the music_xml to import
            auto_format (bool, optional): Auto format the score with the hierarchy score, parts, measures, voices. Defaults to True.
            produce_trees (bool, optional): Produce the BT and TT for each measure. Defaults to False.
        """
        self.m21_score = m21.converter.parse(str(Path(musicxml_path)))
        self.produce_trees = produce_trees
        if auto_format:
            m21u.reconstruct(self.m21_score)

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

    def get_timelines(self):
        # return one timeline for each voice.
        # TODO: Consider all voices, for now works with only the first of each part
        # TODO: merge if there are continuations at the beginning of the measures
        timelines = []
        for ip, p in enumerate(self.m21_score.parts):
            voice_tim = None  # empty timeline for the voice
            for im, m in enumerate(p.getElementsByClass(m21.stream.Measure)):
                # consider only the first voice (TO UPDATE)
                voice = m.getElementsByClass(m21.stream.Voice)[0]
                gn_list = voice.getElementsByClass(m21.note.GeneralNote)
                m_tim = m21u.m21_2_timeline(gn_list).shift_and_rescale(
                    0, 1
                )  # force each measure to be in the interval 0-1
                voice_tim = m_tim if voice_tim is None else voice_tim + m_tim
            timelines.append(voice_tim)
        return timelines

    def get_timelines_json(self):
        out_json = {"name": "piece_name", "grammar": "grammar_name", "voices": []}
        for tim in self.get_timelines():
            out_json["voices"].append(tim.to_json("duration"))
        return out_json

