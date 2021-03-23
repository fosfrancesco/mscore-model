# This cose is used to communicate with the NEUMA server.
# It's currently used for testing and development purposes and may be moved in the future.
from score_model.music_sequences import Timeline, MusicalContent

import requests
import json


def send_to_qparse(musical_content: MusicalContent, grammar: str):
    # api-endpoint
    URL = "http://neuma.huma-num.fr/rest/transcription/_qparse/"

    # extract info from the musical content
    data = musical_content.to_json("duration")
    # add grammar and name information
    data["name"] = "test_piece"
    data["grammar"] = grammar

    # sending get request and saving the response as response object
    r = requests.request(method="get", url=URL, data=json.dumps(data))

    # extracting data in json format
    data = r.json()
    return data

