# This cose is used to communicate with the NEUMA server.
# It's currently used for testing and development purposes and may be moved in the future.
from score_model.music_sequences import Timeline, MusicalContent

import requests
import json
import uuid


def send_to_qparse(musical_content: MusicalContent, grammar: str):
    # api-endpoint
    URL = "http://neuma.huma-num.fr/rest/transcription/_qparse/"

    # extract info from the musical content
    data = musical_content.to_json("duration")
    # add grammar and name information
    data["name"] = "testpython"
    data["grammar"] = grammar

    # sending get request and saving the response as response object
    r = requests.request(method="get", url=URL, data=json.dumps(data))

    # extracting data in json format
    data = r.json()
    return data


def grammar_txt2json(txt: str) -> dict:
    out = {}
    lines = txt.split("\n")
    # strip comments
    lines = [l.split("//")[0].strip() for l in lines]
    # strip empty lines
    lines = [l for l in lines if len(l) > 0]
    # add general informations
    out["name"] = str(uuid.uuid1())
    out["initial_state"] = 0
    out["meter_numerator"] = int(
        [l for l in lines if l.startswith("[timesig")][0]
        .replace("[", "")
        .replace("]", "")
        .split()[1]
    )
    out["meter_denominator"] = int(
        [l for l in lines if l.startswith("[timesig")][0]
        .replace("[", "")
        .replace("]", "")
        .split()[2]
    )
    out["ns"] = out["name"]
    out["type_weight"] = "probability" if "probability" in lines[0] else "penalty"
    # add rules
    out["rules"] = []
    rule_lines = [l for l in lines if l[0].isdigit()]
    for r in rule_lines:
        out["rules"].append(rule_txt2json(r))
    return out


def rule_txt2json(rule_txt: str) -> dict:
    components = rule_txt.split()
    head = components[0]
    symbol = components[2].split("(")[0]
    weight = components[-1]
    # get the content between parenthesis if it exist
    body = []
    if rule_txt.find("(") >= 0:
        par_content = rule_txt[rule_txt.find("(") + 1 : rule_txt.find(")")]
        par_content = par_content.replace(" ", "").split(",")
        for b in par_content:
            if ":" in b:  # rule with a certain multeplicity
                body.append(
                    {"state": int(b.split(":")[0]), "occ": int(b.split(":")[1])}
                )
            else:  # multeplicity default 1
                body.append({"state": int(b), "occ": 1})
    return {
        "head": int(head),
        "body": body,
        "weight": float(weight),
        "symbol": symbol,
    }
