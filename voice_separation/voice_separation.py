import music21 as m21
from configuration import Configuration
from consistency import get_voices
from time import time
import math

dataset = {
    '/Users/lyrodrig/datasets/voicesep',
}

def get_notes(score, start_offset, end_offset):
    """Creates a dict mapping the notes of a score in interval [start_offset, end_offset].

    Args:
        score: a m21.stream.Score
        start_offset: beginning offset of the score we want to get the notes
        end_offset: the last offset of the score we want to get the notes

    Returns: 
        A dict that maps offset to a list of notes beginning at the offset in the score.

    """
    scoreTree = m21.tree.fromStream.asTimespans(score, flatten=True, classList=(m21.note.Note, m21.chord.Chord))

    current_offset = start_offset
    notes_by_offset = {}

    while current_offset is not None and current_offset <= end_offset:
        verticality = scoreTree.getVerticalityAt(current_offset)
        notes_by_offset[current_offset] = []
        elements = [timespan.element for timespan in verticality.startTimespans]
        for element in elements:
            if isinstance(element, m21.chord.Chord):
                for note in element:
                    note.offset = current_offset
                    notes_by_offset[current_offset].append(note)
            else:
                element.offset = current_offset
                notes_by_offset[current_offset].append(element)
        current_offset = verticality.nextStartOffset

    return notes_by_offset


def separate_voices(score, start_offset, end_offset):
    """ Separate voices from score in interval [start_offset, end_offset] 
    
    Args:
        score: a m21.stream.Score
        start_offset: beginning offset of the score we want to get the notes
        end_offset: the last offset of the score we want to get the notes

    Returns:
        A new score with 
    """
    notes_by_offset = get_notes(score, start_offset, end_offset)

    # initialization
    solutions = {}
    # TODO make get_all_configs not a class method...
    initial_config = Configuration() # an empty config to initiate the algorithm from

    for offset, notes in notes_by_offset.items():
        #print("#####################################################################")
        #print("OFFSET", offset)
        #print(notes)
        # get all the configurations that can 
        solutions[offset] = initial_config.get_all_configs(notes, offset)
        
        # calculate the horizontal cost of newly created 
        # configurations and configurations at previous offset,
        # except of there is no previous offset (offset == start_offset).

        if offset > start_offset:
            for right_config in solutions[offset]:
                for left_config in solutions[prev_offset]:
                    right_config.calculate_horizontal_cost(left_config)
                right_config.calculate_cost()            
        else:
            # this ensures that the configs at offset == start_offset don't have empty voices
            # otherwise the notes at this offset would be ignored.

            for config in solutions[offset]:
                config.make_voices()
        prev_offset = offset
    
    # The result of the algorithm is the one with the smallest cost
    # in the last list of configurations.

    min_cost = math.inf
    for config in solutions[end_offset]:
        if min_cost > config.cost:
            res_config = config
            min_cost = config.cost
    #res_config.print()

    # turn the result configuration into a stream
    return res_config.to_stream()

def test_voice_separation(xml_score, midi_score):
    original_score = get_voices(xml_score)
    our_score = separate_voices(midi_score, 0.0, 3.0)
    our_score.show('t')

    # TODO
    return


xml_file_name = '/Users/lyrodrig/datasets/asap-dataset/Bach/Italian_concerto/midi_score.mid'
midi_file_name = '/Users/lyrodrig/datasets/asap-dataset/Bach/Italian_concerto/xml_score.musicxml'

xml_score = m21.converter.parse(xml_file_name)
midi_score = m21.converter.parse(midi_file_name)
test_voice_separation(xml_score, midi_score)


#config = separate_voices(score, 0.0, 2.0)
#config.show('t')
"""
file_name = '/Users/lyrodrig/datasets/asap-dataset/Bach/Italian_concerto/xml_score.musicxml'
score = m21.converter.parse(file_name)
score.makeVoices(inPlace=True)
#score.show('t')
print(len(score.getElementsByClass('Voice')))

new_stream = m21.stream.Stream()
score = score.voicesToParts()
for part in score.parts:
    new_stream.insert(part.flat)

new_stream.show('t')
print(len(new_stream))
"""
"""
print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
for config in voices:
    config.print()

print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
"""
