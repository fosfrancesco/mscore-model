from score_model.server_communication import send_to_qparse
from score_model.music_sequences import Timeline, MusicalContent, Event
from score_model.constant import REST_SYMBOL

import numpy as np
from fractions import Fraction


def test_send_to_qparse():
    # first timeline
    timestamps1 = np.array([0, Fraction(1, 3), 1])
    musical_artifacts1 = np.array([["C1", "C2"], REST_SYMBOL, ["E2"]])
    events1 = [Event(t, m) for t, m in zip(timestamps1, musical_artifacts1)]
    tim1 = Timeline(events1, start=0, end=2)
    # second timeline
    timestamps2 = np.array([0, Fraction(1, 2)])
    musical_artifacts2 = np.array([["A1"], ["A2"]])
    events2 = [Event(t, m) for t, m in zip(timestamps2, musical_artifacts2)]
    tim2 = Timeline(events2, start=0, end=1)
    # create musical content
    mc = MusicalContent([tim1, tim2])
    # call qparse api
    api_return = send_to_qparse(mc, "test2")
    expected_json = {
        "name": "test_piece",
        "grammar": "test2",
        "voices": [["B3(FAIL, FAIL, FAIL) ", "FAIL "], ["B3(FAIL, FAIL, FAIL) "],],
    }
    assert len(api_return["voices"][0]) == 2
    assert len(api_return["voices"][1]) == 1
    assert api_return == expected_json
