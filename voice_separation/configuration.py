import music21 as m21
from copy import copy, deepcopy
from itertools import combinations
import math
from cost_constants import *


class Configuration:
    """ Class representing the list of voices at a certain offset. 

    Initially, a configuration is just the notes at an offset, mapped into several voices.
    Each configuration has vertical cost calculated by how the notes are spread.
    Then, for each configuration at previous offset, a horizontal cost is calculated.
    To create the voices, we take the previous configuration with the smallest cost,
    and add the notes in this configuration's spread.
    
    Attributes:
        offset: Offset of the config.
        spread: A dict mapping voice number to a list of notes.
        monophonic: A boolean indicating if the voices must be monophonic or not.
        horizontal_cost: A dict mapping configurations at previous offset to their cost comparing to this one.
        cost: The cost of this configuration.
        voices: List of m21.stream.Voice created from the best previous configuration and the notes in spread of this Configuration.
    """

    def __init__(self, offset=-1, spread=[], parameters=[]):
        self.offset = offset
        self.spread = spread
        self.monophonic = False
        if offset > -1:
            self.calculate_vertical_cost()
        self.horizontal_cost = {}
        self.cost = 0
        self.voices = {}
        for voice_nb in range(1, MAX_VOICES+1):
            self.voices[voice_nb] = m21.stream.Voice()

    def get_all_configs(self, notes, offset, note_config={}):
        """Takes a list of notes and creates a list of configurations for each combination of notes possible. """
        # Stop condition
        if notes == []:
            return Configuration(offset, note_config)

        # Initialization
        if note_config == {}:
            for index in range(1, MAX_VOICES+1):
                note_config[index] = []

        configs = []
        current_note = notes[0]

        # Recursion
        for index in range(1, MAX_VOICES+1):
            new_note_config = self.copy(note_config)
            new_note_config[index].append(current_note)

            new_config_list = self.get_all_configs(
                notes[1:],
                offset,
                new_note_config)
            # this is so we have a flat list of configurations
            if isinstance(new_config_list, list):
                for item in new_config_list: configs.append(item)
            else: configs.append(new_config_list)

        return configs

    def get_offset(self):
        return self.offset

    def copy(self, dictionary):
        result = {}
        for key, value in dictionary.items():
            result[key] = copy(value)
        return result

    def make_voices(self):
        for voice_nb, notes in self.spread.items():
            for note in notes:
                self.voices[voice_nb].insert(note)

    def calculate_cost(self):
        """Finds the previous configurations with the lowest cost, updates the cost, and creates the voice."""
        min_cost = math.inf
        if self.horizontal_cost:
            best_config = list(self.horizontal_cost.keys())[0]
        else:
            return

        for config, cost in self.horizontal_cost.items():
            if min_cost > cost:
                min_cost = cost
                best_config = config
        self.cost = min_cost + self.vertical_cost
        self.update_voices(best_config)

    def update_voices(self, config):
        """ Creates a list of voices from another config, and this configuration's note spread."""
        self.voices = deepcopy(config.voices)
        for voice_number, stream in self.voices.items():
            for note in self.spread[voice_number]:
                stream.insert(note)

    def calculate_vertical_cost(self):
        """Calculates the vertical cost's of the note spread."""
        cost = 0
        for voice_index, notes in self.spread.items():
            if self.monophonic and len(notes) > 1: cost = math.inf
            cost = cost + voice_index * len(notes)
            cost = cost + self._calculate_chord_width(notes)

        voice_tuples = []
        for key in self.spread.keys():
            voice_tuples = voice_tuples + [(key, v) for v in self.spread[key]]

        # get all the combinations of the tuples in array
        note_pairs = [tuple for tuple in combinations(voice_tuples, 2)]
        
        for pair in note_pairs:
            cost = cost + self._calculate_voice_cross_cost(pair)
            cost = cost + self._calculate_length_cost(pair)
            cost = cost + self._calculate_tonal_fusion_cost(pair)

        self.vertical_cost = cost

    def get_last_notes(self, voice_nb):
        """Get the last notes of each voice."""
        stream = self.voices[voice_nb]
        last_notes = stream.getElementsByOffset(
            stream.highestOffset)
        return list(last_notes)

    def calculate_horizontal_cost(self, config):
        """Calculates the cost between a configuration and this configuration."""
        # ignore inf costs
        if config.vertical_cost == math.inf: return
        cost = 0.0
        for voice_index, notes in self.spread.items():
            last_notes = config.get_last_notes(voice_index)
            if not isinstance(last_notes, list):
                last_notes = [last_notes]
            if last_notes is []:
                cost = cost + NEW_VOICE_COST

            for note in notes:
                for last_note in last_notes:
                    cost = cost + \
                        self._calculate_rest_cost(last_note, note)
                    cost = cost + \
                        self._calculate_overlap_cost(last_note, note)
                    cost = cost + \
                        self._calculate_pitch_proximity_cost(last_note, note)
                    cost = cost + \
                        self._calculate_duration_cost(last_note, note)
        if not cost: cost = EMPTY_VOICE_COST
        self.horizontal_cost[config] = cost

    def _calculate_chord_width(self, notes):
        if len(notes) <= 1: return 0
        notes.sort()
        range = abs(notes[0].pitch.midi - notes[-1].pitch.midi)
        if range > 15:
            return CHORD_WIDTH_COST
        return 0

    def _calculate_duration_cost(self, last_note, note):
        if not note.quarterLength or not last_note.quarterLength:
            return 0
        if last_note.quarterLength % note.quarterLength or \
                note.quarterLength % last_note.quarterLength:
            return 0
        return DURATION_COST + abs(note.quarterLength - last_note.quarterLength) * 10

    def _calculate_tonal_fusion_cost(self, pair):
        return 0

    def _calculate_voice_cross_cost(self, pair):
        first_note = pair[0]
        second_note = pair[1]
        if (first_note[0] > second_note[0] and first_note[1] > second_note[1]) \
                or (first_note[0] < second_note[0] and first_note[1] < second_note[1]):
            return VOICE_CROSSING_COST
        return 0

    def _calculate_length_cost(self, pair):
        first_note = pair[0]
        second_note = pair[1]
        if (first_note[0] == second_note[0] and first_note[1].quarterLength != second_note[1].quarterLength):
            return DIFFERENT_LENGTH_COST
        return 0

    def _calculate_pitch_proximity_cost(self, last_note, note):
        return self.get_distance(last_note, note)

    # Assign 6 for each pair of consecutive notes with the same voice label having a temporal gap(penalize rests).
    def _calculate_rest_cost(self, prev_note, current_note):
        if prev_note.offset + prev_note.quarterLength < current_note.offset:
            return REST_COST
        return 0

    # Assign 7 for each pair of consecutive notes with the same voice label that temporally overlap.
    def _calculate_overlap_cost(self, prev_note, current_note):
        if prev_note and prev_note.quarterLength > current_note.offset:
            return OVERLAP_COST
        return 0

    def get_cost(self):
        return self.cost

    def get_distance(self, note1, note2):
        return abs(note1.pitch.midi - note2.pitch.midi)

    def to_stream(self):
        stream = m21.stream.Score()
        for voice_nb, voice in self.voices.items():
            voice.id = voice_nb
            stream.insert(voice)
        return stream

    def print(self):
        print("___________________________________")
        print("\toffset :", self.offset)
        print("Configuration with cost  : ", self.cost)
        print("\tvertical cost :", self.vertical_cost)
        print("\thorizontal cost :", self.horizontal_cost)
        #print("voices:", self.voices)
        for voice_nb, stream in self.voices.items():
            print("Voix ", voice_nb)
            for note in stream.notes:
                print("\tnote", note.pitch, "\toffset", note.offset,
                      "\tlength", note.quarterLength)


        print(self.spread)
        print("___________________________________")
        print()
