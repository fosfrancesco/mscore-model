import music21 as m21
from pathlib import Path
import score_model


def test_get_timelines():
    score = score_model.ScoreModel("tests/test_musicxml/test_score1.musicxml")
    timelines = score.get_timelines()
    assert len(timelines) == 1
    assert timelines[0].start == 0
    assert timelines[0].end == 7


def test_get_timelines2():
    score = score_model.ScoreModel("tests/test_musicxml/test_multipart.musicxml")
    timelines = score.get_timelines()
    assert len(timelines) == 2
    assert timelines[0].start == 0
    assert timelines[0].end == 2


def test_get_timelines_json():
    score = score_model.ScoreModel("tests/test_musicxml/test_multipart.musicxml")
    out_json = score.get_timelines_json()
    expected_json = {
        "name": "piece_name",
        "grammar": "grammar_name",
        "voices": [
            [
                {
                    "duration": {"numerator": 1, "denominator": 2},
                    "musical_artifact": [62],
                },
                {
                    "duration": {"numerator": 1, "denominator": 2},
                    "musical_artifact": [64],
                },
                {
                    "duration": {"numerator": 1, "denominator": 1},
                    "musical_artifact": [65],
                },
            ],
            [
                {
                    "duration": {"numerator": 1, "denominator": 4},
                    "musical_artifact": [62, 67, 74],
                },
                {
                    "duration": {"numerator": 1, "denominator": 4},
                    "musical_artifact": [67],
                },
                {
                    "duration": {"numerator": 1, "denominator": 4},
                    "musical_artifact": [67],
                },
                {
                    "duration": {"numerator": 1, "denominator": 4},
                    "musical_artifact": [65],
                },
                {"duration": {"numerator": 1, "denominator": 2}, "musical_artifact": 0},
                {
                    "duration": {"numerator": 1, "denominator": 2},
                    "musical_artifact": [65],
                },
            ],
        ],
    }
    assert out_json == expected_json

