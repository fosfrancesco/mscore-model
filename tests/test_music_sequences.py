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
    tim = Timeline(timestamps, musical_artifacts)
    assert tim.events == [(1, "C1"), (2, "D2"), (6.5, "F4")]
    assert np.array_equal(tim.get_musical_artifacts(), musical_artifacts)
    assert np.array_equal(tim.get_timestamps(), timestamps)
