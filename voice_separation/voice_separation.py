import music21 as m21
from configuration import Configuration, Parameters
from consistency import score_compare
from time import time
import math
from scipy import optimize
import os
import random
import json


def timer_func(func):

    def function_timer(*args, **kwargs):
        start = time()
        value = func(*args, **kwargs)
        end = time()
        runtime = end - start
        msg = "{func} took {time} seconds to complete its execution."
        print(msg.format(func=func.__name__, time=runtime))
        return value
    return function_timer

def get_measure(score, measure_nb):
    """Returns a measure of a score according to its number. 
    
    Args:
        score:  a m21.stream.Score
        measure_nb: an int refering to the measure number

    Returns:
        an m21.stream.Score() containing only the measure, 
        the very first offset number of the measure,
        and the very last offset number of the measure.
    """
    min_offset = math.inf
    max_offset = 0
    new_score = m21.stream.Score()
    
    for part in score.parts:
        measure = part.measure(measure_nb)
        if measure is None: return (None, None, None)
        measure = measure.getElementsByClass('Voice')

        for voice in measure:
            min_offset = min(min_offset, voice.lowestOffset)
            max_offset = max(max_offset, voice.highestOffset)

            new_score.insert(voice)
    # not useful but makes it prettier !
    for voice, i in zip(new_score, range(1, len(new_score)+1)):
        voice.id = i 
    return (new_score, min_offset, max_offset)


def get_number_measures(score):
    return len(score.parts[0].getElementsByClass('Measure'))


def get_number_of_voices(score):
    return len(score.parts)


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
        if current_offset == start_offset:
            elements = [timespan.element for timespan in verticality.startAndOverlapTimespans]
            if elements == []:
                start_offset = verticality.nextStartOffset
        else:
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

    return (start_offset, current_offset, notes_by_offset)


def separate_voices(score, start_offset, end_offset, parameters, monophonic=True):
    """Separates voices from score in interval [start_offset, end_offset].

    Using an interval allows to test the voice separation either for a whole score,
    only a measure, or just an excerpt.
    
    Args:
        score: a m21.stream.Score
        start_offset: beginning offset of the score we want to get the notes
        end_offset: the last offset of the score we want to get the notes

    Returns:
        A new score with the voices separated.
    """
    start_offset, end_offset, notes_by_offset = get_notes(score, start_offset, end_offset)

    # initialization
    solutions = {}
    # TODO make get_all_configs not a class method...
    if not isinstance(parameters, Parameters):
        parameters = Parameters(param_list=parameters)
    initial_config = Configuration(parameters) # an empty config to initiate the algorithm from

    for offset, notes in notes_by_offset.items():
        # get all the configurations possible
        if notes == []: 
            prev_offset = offset
            continue
        solutions[offset] = initial_config.get_all_configs(notes, offset, monophonic)
        
        # calculate the horizontal cost of newly created 
        # configurations and configurations at previous offset,
        # except of there is no previous offset (offset == start_offset).

        if offset > start_offset:
            if solutions[offset] and solutions[prev_offset]:
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
        last_offset = offset
    
    # The result of the algorithm is the one with the smallest cost
    # in the last list of configurations.

    min_cost = math.inf
    res_config = solutions[last_offset][0]
    for config in solutions[last_offset]:
        if min_cost > config.cost:
            res_config = config
            min_cost = config.cost
    # turn the result configuration into a stream
    return res_config.to_stream()


@timer_func
def separate_voices_score(score, compare=True, parameters=Parameters(), verbose=True):
    """Separates the voices from the score, one measure at a time.
    
    Args:
        score: a m21.stream.Score
        compare: a boolean that is True if the score is already separated in voices
        parameters: values for different parameters

    Returns:
        If compare is False, then it returns a score with the voice separated
        If compare is True, then it returns a score, and the comparison score.
    """
    nb_measures = get_number_measures(score)
    new_score = m21.stream.Score()
    total_cost = 0

    for nb in range(0, nb_measures):
        measure, start_offset, end_offset = get_measure(score, nb)
        # if measure doesn't exist, continue (for example : no 0 measure (no anacrusis))
        if measure is None:
            continue

        voices = separate_voices(measure, start_offset, end_offset, parameters)
        new_score.append(m21.stream.Measure(voices, number=nb))

        if compare:
            total_cost += score_compare(measure, voices)
        if verbose:
            print("Measure :", nb)
            print("\tCost :", total_cost)

    print("Result for this score :", total_cost)

    if compare:
        return (new_score, total_cost)
    return new_score


@timer_func
def separate_voices_dir(dir_path, compare=True, extensions=['.mei', '.musicxml', '.mid']):
    """Separates the voices of each file in a directory.

    Args:
        dir_path: a string of the directory path
        compare: a boolean that is True if the score is already separated in voices, and thus can be compared
        extensions: a list of extensions of the files that should be parsed

    Returns: TODO
        Writes in a json file (results.json) each file and the result of the comparison.
    """
    files = [os.path.join(root, name)
             for root, dirs, files in os.walk(dir_path)
             for name in files
             if name.endswith((extensions))]

    i = 1
    file_result = {}
    for file in files[:20]:
        print('FILE', i, 'out of', len(files))
        print(file)
        i += 1

        score = m21.converter.parse(file)
        # find nb of voices
        nb_voices = get_number_of_voices(score)
        print('Nb of voices: ', nb_voices)

        # focus on scores with at most 4 voices
        if nb_voices < 5:
            score, total_cost = separate_voices_score(
                score, parameters=Parameters(max_voices=nb_voices))
            file_result[total_cost] = file

    with open('results.json', 'w') as outfile:
        json.dump(file_result, outfile, indent=4, sort_keys=True)


# this is the function used by the grid search
def cost(x, *params):
    score, start_offset, end_offset = params
    voices = separate_voices(score, start_offset, end_offset, x)
    return score_compare(score, voices)


def grid_search(score, start_offset, end_offset, step):
    rranges = (slice(0, 100, step), slice(0, 100, step), slice(0, 100, step),
               slice(0, 100, step),
               )
    res_brute = optimize.brute(cost, rranges, args=(score, start_offset, end_offset),
                               full_output=True, finish=optimize.fmin)

    print(res_brute[0])
    print(res_brute[1])
    return res_brute[0]



dir_path = 'tests/test_voice_sep/'
separate_voices_dir(dir_path, extensions='.mei')


