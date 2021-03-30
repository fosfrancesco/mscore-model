from score_model.music_sequences import (
    split_content,
    musical_split,
    Event,
    Timeline,
    MusicalContent,
)
from score_model.constant import CONTINUATION_SYMBOL, REST_SYMBOL

import numpy as np
from fractions import Fraction


def test_equally_split1():
    seq = [0.1, 0.2, 0.7]
    output = split_content(seq, 2)
    expected_output = [[0.1, 0.2], [0.7]]
    for o, exp_o in zip(output, expected_output):
        assert np.array_equal(o, exp_o)
    seq = [0.1, 0.5, 0.7]
    output = split_content(seq, 2)
    expected_output = [[0.1], [0.5, 0.7]]
    for o, exp_o in zip(output, expected_output):
        assert np.array_equal(o, exp_o)
    seq = [0, 0.1, 0.34]
    output = split_content(seq, 3)
    expected_output = [[0, 0.1], [0.34], []]
    for o, exp_o in zip(output, expected_output):
        assert np.array_equal(o, exp_o)


def test_equally_split2():
    seq = [0, 2]
    output = split_content(seq, 2, (0, 4))
    expected_output = [[0], [2]]
    for o, exp_o in zip(output, expected_output):
        assert np.array_equal(o, exp_o)
    seq = [2, 3]
    output = split_content(seq, 2, (2, 4))
    expected_output = [[2], [3]]
    for o, exp_o in zip(output, expected_output):
        assert np.array_equal(o, exp_o)


def test_musical_split1():
    seq = [0, 0.25, 0.75]
    output = musical_split(seq, 2)
    expected_output = [[0, 0.5], [0, 0.5]]
    for o, exp_o in zip(output, expected_output):
        assert np.array_equal(o, exp_o)
    seq = [0, 0.25]
    output = musical_split(seq, 3)
    expected_output = [[0, 0.75], [0], [0]]
    for o, exp_o in zip(output, expected_output):
        assert np.array_equal(o, exp_o)


def test_timeline1():
    timestamps = np.array([1, 2, 6.5])
    musical_artifacts = np.array(["C1", "D2", "F4"])
    events = [Event(0, CONTINUATION_SYMBOL)] + [
        Event(t, m) for t, m in zip(timestamps, musical_artifacts)
    ]
    tim = Timeline(events, start=0, end=8)
    assert np.array_equal(tim.events, events)
    assert tim.get_musical_artifacts() == [CONTINUATION_SYMBOL, "C1", "D2", "F4"]
    assert tim.get_timestamps() == [0, 1, 2, 6.5]


def test_split_timeline1():
    timestamps = np.array([0, 0.25, 0.75])
    musical_artifacts = np.array(["C1", "D2", "F4"])
    events = [Event(t, m) for t, m in zip(timestamps, musical_artifacts)]
    tim = Timeline(events)
    expected_timelines = [
        Timeline([Event(0, "C1")], start=0, end=0.25),
        Timeline([Event(0.25, "D2")], start=0.25, end=0.5),
        Timeline([Event(0.5, CONTINUATION_SYMBOL)], start=0.5, end=0.75),
        Timeline([Event(0.75, "F4")], start=0.75, end=1.0),
    ]
    assert tim.split(4) == expected_timelines


def test_split_timeline2():
    timestamps = np.array([0, 1, 7, 7.5])
    musical_artifacts = np.array(["C1", "D2", "F4", "F5"])
    events = [Event(t, m) for t, m in zip(timestamps, musical_artifacts)]
    tim = Timeline(events, start=0, end=8)
    expected_timelines = [
        Timeline([Event(0, "C1"), Event(1, "D2")], start=0, end=2),
        Timeline([Event(2, CONTINUATION_SYMBOL)], start=2, end=4),
        Timeline([Event(4, CONTINUATION_SYMBOL)], start=4, end=6),
        Timeline(
            [Event(6, CONTINUATION_SYMBOL), Event(7, "F4"), Event(7.5, "F5")],
            start=6,
            end=8,
        ),
    ]
    assert np.array_equal(tim.split(4), expected_timelines)


def test_split_timeline3():
    # testing the timeline split with normalize = True
    timestamps = np.array([0, 1, 2.5, 3])
    musical_artifacts = np.array(["C1", "D2", "F4", "F5"])
    events = [Event(t, m) for t, m in zip(timestamps, musical_artifacts)]
    tim = Timeline(events, start=0, end=4)
    expected_timelines = [
        Timeline([Event(0, "C1")], start=0, end=4),
        Timeline([Event(0, "D2")], start=0, end=4),
        Timeline([Event(0, CONTINUATION_SYMBOL), Event(2, "F4")], start=0, end=4),
        Timeline([Event(0, "F5")], start=0, end=4),
    ]
    assert np.array_equal(tim.split(4, normalize=True), expected_timelines)


def test_split_timeline4():
    # testing the timeline split with start > 0
    timestamps = np.array([1, 1 + Fraction(1, 3)])
    musical_artifacts = np.array(["C1", "D2"])
    events = [Event(t, m) for t, m in zip(timestamps, musical_artifacts)]
    tim = Timeline(events, start=1, end=2)
    expected_timelines = [
        Timeline([Event(1, "C1"), Event(1 + Fraction(1, 3), "D2")], start=1, end=1.5),
        Timeline([Event(1.5, CONTINUATION_SYMBOL)], start=1.5, end=2),
    ]
    assert np.array_equal(tim.split(2), expected_timelines)


def test_split_timeline5():
    # testing the timeline split with normalize = True and start > 0
    timestamps = np.array([1, 1 + Fraction(1, 3)])
    musical_artifacts = np.array(["C1", "D2"])
    events = [Event(t, m) for t, m in zip(timestamps, musical_artifacts)]
    tim = Timeline(events, start=1, end=2)
    expected_timelines = [
        Timeline([Event(1, "C1"), Event(1 + Fraction(2, 3), "D2")], start=1, end=2),
        Timeline([Event(1, CONTINUATION_SYMBOL)], start=1, end=2),
    ]
    assert np.array_equal(tim.split(2, normalize=True), expected_timelines)


def test_shift_and_rescale():
    # testing the timeline rescale function
    timestamps = np.array([1, 1 + Fraction(1, 3)])
    musical_artifacts = np.array(["C1", "D2"])
    events = [Event(t, m) for t, m in zip(timestamps, musical_artifacts)]
    tim = Timeline(events, start=1, end=2)
    expected_timeline = Timeline(
        [Event(6, "C1"), Event(6 + Fraction(2, 3), "D2")], start=6, end=8
    )
    assert np.array_equal(
        tim.shift_and_rescale(new_start=6, new_end=8), expected_timeline
    )


def test_timeline_export_json():
    # testing the timeline export json function
    timestamps = np.array([1, 1 + Fraction(1, 3)])
    musical_artifacts = np.array([["C1", "C2"], REST_SYMBOL])
    events = [Event(t, m) for t, m in zip(timestamps, musical_artifacts)]
    tim = Timeline(events, start=1, end=2)
    expected_json = [
        {
            "duration": {"numerator": 1, "denominator": 3,},
            "musical_artifact": ["C1", "C2"],
        },
        {
            "duration": {"numerator": 2, "denominator": 3,},
            "musical_artifact": REST_SYMBOL,
        },
    ]
    assert tim.to_json("duration") == expected_json


def test_timeline_export_json2():
    # testing the timeline export json function
    timestamps = np.array([0, Fraction(1, 3), 1])
    musical_artifacts = np.array([["C1", "C2"], REST_SYMBOL, ["E2"]])
    events = [Event(t, m) for t, m in zip(timestamps, musical_artifacts)]
    tim = Timeline(events, start=0, end=2)
    expected_json = [
        {
            "duration": {"numerator": 1, "denominator": 3},
            "musical_artifact": ["C1", "C2"],
        },
        {
            "duration": {"numerator": 2, "denominator": 3},
            "musical_artifact": REST_SYMBOL,
        },
        {"duration": {"numerator": 1, "denominator": 1}, "musical_artifact": ["E2"]},
    ]
    assert tim.to_json("duration") == expected_json


def test_timeline_export_json3():
    # testing the timeline export json function
    timestamps = np.array([0, Fraction(1, 3), 1])
    musical_artifacts = np.array([["C1", "C2"], REST_SYMBOL, ["E2"]])
    events = [Event(t, m) for t, m in zip(timestamps, musical_artifacts)]
    tim = Timeline(events, start=0, end=2)
    expected_json = [
        {
            "onset": {"numerator": 0, "denominator": 1},
            "musical_artifact": ["C1", "C2"],
        },
        {"onset": {"numerator": 1, "denominator": 3}, "musical_artifact": REST_SYMBOL,},
        {"onset": {"numerator": 1, "denominator": 1}, "musical_artifact": ["E2"]},
    ]
    assert tim.to_json("onset") == expected_json


def test_timeline_export_json4():
    # testing the timeline export json function with start != 0
    timestamps = np.array([1, Fraction(3, 2)])
    musical_artifacts = np.array([["C1", "C2"], ["E2"]])
    events = [Event(t, m) for t, m in zip(timestamps, musical_artifacts)]
    tim = Timeline(events, start=1, end=2)
    expected_json = [
        {
            "duration": {"numerator": 1, "denominator": 2},
            "musical_artifact": ["C1", "C2"],
        },
        {"duration": {"numerator": 1, "denominator": 2}, "musical_artifact": ["E2"],},
    ]
    assert tim.to_json("duration") == expected_json


def test_timeline_add():
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

    expected_timeline_events = [["C1", "C2"], REST_SYMBOL, ["E2"], ["A1"], ["A2"]]
    expected_timeline_onsets = [0, Fraction(1, 3), 1, 2, Fraction(5, 2)]

    added_tim = tim1 + tim2
    assert (
        list([e.musical_artifact for e in added_tim.events]) == expected_timeline_events
    )
    assert list([e.timestamp for e in added_tim.events]) == expected_timeline_onsets
    assert added_tim.start == 0
    assert added_tim.end == 3


def test_musical_content():
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
    # third timeline
    timestamps3 = np.array([1, Fraction(3, 2)])
    musical_artifacts3 = np.array([["A1"], ["A2"]])
    events3 = [Event(t, m) for t, m in zip(timestamps3, musical_artifacts3)]
    tim3 = Timeline(events3, start=1, end=2)
    # create musical content
    mc = MusicalContent([tim1, tim2, tim3])
    expected_json = {
        "voices": [
            [  # first voice
                {
                    "duration": {"numerator": 1, "denominator": 3},
                    "musical_artifact": ["C1", "C2"],
                },
                {
                    "duration": {"numerator": 2, "denominator": 3},
                    "musical_artifact": REST_SYMBOL,
                },
                {
                    "duration": {"numerator": 1, "denominator": 1},
                    "musical_artifact": ["E2"],
                },
            ],
            [  # second voice
                {
                    "duration": {"numerator": 1, "denominator": 2},
                    "musical_artifact": ["A1"],
                },
                {
                    "duration": {"numerator": 1, "denominator": 2},
                    "musical_artifact": ["A2"],
                },
            ],
            [  # third voice
                {
                    "duration": {"numerator": 1, "denominator": 2},
                    "musical_artifact": ["A1"],
                },
                {
                    "duration": {"numerator": 1, "denominator": 2},
                    "musical_artifact": ["A2"],
                },
            ],
        ]
    }
    assert mc.to_json("duration") == expected_json
