from lib.music_sequences import *


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
