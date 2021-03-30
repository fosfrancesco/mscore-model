from score_model.server_communication import (
    send_to_qparse,
    rule_txt2json,
    grammar_txt2json,
)
from score_model.music_sequences import Timeline, MusicalContent, Event
from score_model.constant import REST_SYMBOL

import numpy as np
from fractions import Fraction
from pathlib import Path
import json


def test_send_to_qparse_1():
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


def test_send_to_qparse_2():
    # first timeline
    timestamps1 = np.array([0, 1])
    musical_artifacts1 = np.array([["C1", "C2"], ["E2"]])
    events1 = [Event(t, m) for t, m in zip(timestamps1, musical_artifacts1)]
    tim1 = Timeline(events1, start=0, end=2)
    # create musical content
    mc = MusicalContent([tim1])
    # call qparse api
    api_return = send_to_qparse(mc, "test_2_44")
    expected_json = {
        "name": "test_new",
        "grammar": "test_2_44",
        "voices": [["N1", "N1"]],
    }
    assert len(api_return["voices"][0]) == 2
    assert api_return == expected_json


def test_rule_txt2json_1():
    rule_txt = "0 -> U3(1:2, 1)  0.25"
    expected_json = {
        "head": 0,
        "body": [{"state": 1, "occ": 2}, {"state": 1, "occ": 1}],
        "weight": 0.25,
        "symbol": "U3",
    }
    assert rule_txt2json(rule_txt) == expected_json


def test_rule_txt2json_2():
    rule_txt = "1 -> T7(4, 4, 4, 4, 4, 4, 4) 6.95"
    expected_json = {
        "head": 1,
        "body": [
            {"state": 4, "occ": 1},
            {"state": 4, "occ": 1},
            {"state": 4, "occ": 1},
            {"state": 4, "occ": 1},
            {"state": 4, "occ": 1},
            {"state": 4, "occ": 1},
            {"state": 4, "occ": 1},
        ],
        "weight": 6.95,
        "symbol": "T7",
    }
    assert rule_txt2json(rule_txt) == expected_json


def test_rule_txt2json_3():
    rule_txt = "1 -> C0                      0.1"
    expected_json = {
        "head": 1,
        "body": [],
        "weight": 0.1,
        "symbol": "C0",
    }
    assert rule_txt2json(rule_txt) == expected_json


def test_grammar_txt2json_1():
    with open(Path("tests/test_grammars/text/test_1_44.wta"), "r") as file:
        gr_txt = file.read()
    gr_json = grammar_txt2json(gr_txt)
    assert gr_json["meter_numerator"] == 4
    assert gr_json["meter_denominator"] == 4
    assert len(gr_json["rules"]) == 7
    with open(Path("tests/test_grammars/json/test_1_44.json"), "w") as file:
        gr_txt = json.dump(gr_json, file)

