import json
from music21 import *
import operator
import mido
from lib.NoteTree_v2 import MonophonicScoreTrees, NoteNode, ScoreTrees
from lib.m21utils import generalNote_info


# build the levenshtein matrix and compute the total cost to transform one sequence in the other
def iterative_levenshtein(original, compare_to, eq=operator.eq, costs=(1, 1, 1), verbosity=0):
    """
        iterative_levenshtein(s, t) -> ldist
        ldist is the Levenshtein distance between the sequences
        original and compare_to.
        For all i and j, dist[i,j] will contain the Levenshtein
        distance between the first i elements of s and the
        first j elements of t

        eq : (equality_operator) a function that allow for personalized
                            comparison of complex objects, if it's not
                            defined the default operator is used

        costs: a tuple or a list with three integers (d, i, s)
               where d defines the costs for a deletion
                     i defines the costs for an insertion and
                     s defines the costs for a substitution
    """

    ##Compute the matrix and the distance (last element of the matrix)
    rows = len(original) + 1
    cols = len(compare_to) + 1
    deletes, inserts, substitutes = costs

    dist = [[(0, []) for x in range(cols)] for x in range(rows)]
    # source prefixes can be transformed into empty strings
    # by deletions:
    for row in range(1, rows):
        dist[row][0] = (row * deletes, [0])
    # target prefixes can be created from an empty source string
    # by inserting the characters
    for col in range(1, cols):
        dist[0][col] = (col * inserts, [1])

    for col in range(1, cols):
        for row in range(1, rows):
            if eq(original[row - 1], compare_to[col - 1]):
                cost = 0
            else:
                cost = substitutes
            possibilities = [dist[row - 1][col][0] + deletes, dist[row][col - 1][0] + inserts,
                             dist[row - 1][col - 1][0] + cost]
            minimum = min(possibilities)
            if cost == 0:  # no operation were done
                indices = [3]
            else:
                indices = [i for i, v in enumerate(possibilities) if v == minimum]
            dist[row][col] = (minimum, indices)

    ##now compute the path from the matrix
    path_list = recursive_path_finding(dist, rows - 1, cols - 1)

    # for r in range(rows):
    #     print(dist[r])

    if verbosity <= 0:  # return just the cost
        return dist[rows - 1][cols - 1][0]
    elif verbosity == 1:  # return cost and path list
        return dist[rows - 1][cols - 1][0], path_list
    elif verbosity == 2:  # return cost and path list and pretty print the modifications from the initial to the final input
        print("Cost : " + str(dist[rows - 1][cols - 1][0]))
        path_print(path_list, original, compare_to)
        return dist[rows - 1][cols - 1][0], path_list
    elif verbosity == 3: #return the cost and the list of annotations to put in the database
        return dist[rows - 1][cols - 1][0], get_path(path_list, original, compare_to)
    elif verbosity ==4: #return the cost and the path with subtrees
        return dist[rows - 1][cols - 1][0], get_path_subtrees(path_list, original, compare_to)

# Find the shortest distance path from the levenshtain matrix. Find multiple path if there are multiple shortest paths
def recursive_path_finding(cost_path_matrix, row, col):
    path_map = {0: (-1, 0),  # deletion -> move up
                1: (0, -1),  # insertion -> move left
                2: (-1, -1),  # replacement -> move diagonal
                3: (-1, -1)  # no operation done -> move diagonal
                }
    if cost_path_matrix[row][col][1] == []:  # we are at the beginning of the matrix
        return [[(row, col, -1)]]
    else:
        new_paths = []
        addresses = cost_path_matrix[row][col][1]
        for address in cost_path_matrix[row][col][1]:
            recurs_out = recursive_path_finding(cost_path_matrix, row + path_map[address][0],
                                                col + path_map[address][1])
            new_paths.extend(recurs_out)
            for l in range(len(recurs_out)):  # add the current position to all the arrays produced by the recursion
                new_paths[-l - 1].append((row, col, address))
        return new_paths


# An utility to pretty print the shortest paths
def path_print(path_list, original, compare_to, ):
    for path in path_list:
        print("TRANSFORMATION: {}".format(path))
        # the first element say if we add or delete add the beginning
        if path[0][0] > 0:
            for index in range(path[0][0]):
                print("{}. symbol: {} --{}--> {}".format(path[0], original[index], "tra", "[]"))
                print("")
        elif path[0][1] > 0:
            for index in range(path[0][1]):
                print("{}. symbol: {} --{}--> {}".format(path[0], "[]", "tra", compare_to[index]))
        # then process the other elements of the parch
        for index, mod in enumerate(path[1:]):
            if mod[2] == 3:  # no operation
                print("{}. symbol: {} {}".format(mod, original[mod[0] - 1], "nop"))
            elif mod[2] == 2:  # replacement
                print("{}. symbol: {} --{}--> {}".format(mod, original[mod[0] - 1], "rep", compare_to[mod[1] - 1]))
            elif mod[2] == 1:  # insertion
                print("{}. symbol: {} --{}--> {}".format(mod, "[]", "ins", compare_to[mod[1] - 1]))
            elif mod[2] == 0:  # deletion
                print("{}. symbol: {} --{}--> {}".format(mod, original[mod[0] - 1], "del", "[]"))
            else:
                print("{}. symbol: {} --{}--> {}".format(mod, original[mod[0] - 1], "tra", compare_to[mod[1] - 1]))
        print("------------------------------------")


# An utility that return the annotations to be put in the database
def get_path(path_list, original, compare_to, ):
    annotations = list()
    print("Getting path")

    group = 0 #to save in which path is the annotation
    for path in path_list:     #save just the first possible modification
        print("TRANSFORMATION: {}".format(path))
        # then process the other elements of the parch
        for index, mod in enumerate(path[1:]):
            if mod[2] == 3:  # no operation, don't save anything
                print("{}. symbol: {} {}".format(mod, original[mod[0] - 1], "nop"))
            elif mod[2] == 2:  # replacement
                print("{}. symbol: {} --{}--> {}".format(mod, original[mod[0] - 1], "rep", compare_to[mod[1] - 1]))
                annotations.append(("AC_COMP_MODIFICATION",original[mod[0] - 1],compare_to[mod[1] - 1],group))
            elif mod[2] == 1:  # insertion
                print("{}. symbol: {} --{}--> {}".format(mod, "[]", "ins", compare_to[mod[1] - 1]))
                annotations.append(("AC_COMP_INSERTION", original[mod[0] - 1], compare_to[mod[1] - 1], group))
            elif mod[2] == 0:  # deletion
                print("{}. symbol: {} --{}--> {}".format(mod, original[mod[0] - 1], "del", "[]"))
                annotations.append(("AC_COMP_DELETION", original[mod[0] - 1], compare_to[mod[1] - 1], group))
            else:
                raise ValueError("Wrong value in mod[2] : {}".format(mod[2]))
        print("-------------------------")
        group +=1
        # #temporary solution, remove it to have all the paths
        # break
    return annotations

# An utility that return the edit operations with respective subtrees
def get_path_subtrees(path_list, original, compare_to, ):
    annotations = list()
    # print("Getting path subtrees")
    for group, path in enumerate(path_list):   
        # process a specific group of possible operations
        annotations.append([])
        for index, mod in enumerate(path[1:]):
            if mod[2] == 3:  # no operation, don't save anything
                # print("{}. symbol: {} {}".format(mod, original[mod[0] - 1], "nop"))
                annotations[group].append(("nop",original[mod[0] - 1],compare_to[mod[1] - 1]))
            elif mod[2] == 2:  # replacement
                # print("{}. symbol: {} --{}--> {}".format(mod, original[mod[0] - 1], "rep", compare_to[mod[1] - 1]))
                annotations[group].append(("sub",original[mod[0] - 1],compare_to[mod[1] - 1]))
            elif mod[2] == 1:  # insertion
                # print("{}. symbol: {} --{}--> {}".format(mod, "[]", "ins", compare_to[mod[1] - 1]))
                annotations[group].append(("ins", original[mod[0] - 1], compare_to[mod[1] - 1]))
            elif mod[2] == 0:  # deletion

                # print("{}. symbol: {} --{}--> {}".format(mod, original[mod[0] - 1], "del", "[]"))
                annotations[group].append(("del", original[mod[0] - 1], compare_to[mod[1] - 1]))
            else:
                raise ValueError("Wrong value in mod[2]")
        # print("-------------------------")
    return annotations


# personalized function for equality of 2 GeneralNotes or barlines
# 2 notes are equals if both quarterLength and Pitch are the same
def music_eq(elem1, elem2):
    if isinstance(elem1, str) and isinstance(elem2, str):  # 2 barlines
        return True
    elif isinstance(elem1, str) != isinstance(elem2, str):  # one is a barline and the other is not
        return False
    elif elem1.isRest and elem1.isRest: #if we have 2 rest
        return elem1.duration.quarterLength == elem2.duration.quarterLength
    elif elem1.isRest != elem1.isRest: #if one is a rest and the other is not
        return False
    else:  # we have 2 notes
        return (elem1.pitch, elem1.duration.quarterLength) == (elem2.pitch, elem2.duration.quarterLength)


def score_distance(score1, score2):
    """
        Score content edite distance (To remove)    
    """
    flatScore1 = []
    flatScore2 = []
    # import score1
    for part_index, part in enumerate(score1.parts):  # loop through parts
        for measure_index, measure in enumerate(part.getElementsByClass('Measure')):
            if len(measure.voices) == 0:  # there is a single Voice ( == for the library there are no voices)
                flatScore1.extend(list(measure.getElementsByClass('GeneralNote')))
            else:  # there are multiple voices (or an array with just one voice)
                for voice in measure.voices:
                    flatScore1.extend(list(voice.getElementsByClass('GeneralNote')))
    # import score2
    for part_index, part in enumerate(score2.parts):  # loop through parts
        for measure_index, measure in enumerate(part.getElementsByClass('Measure')):
            if len(measure.voices) == 0:  # there is a single Voice ( == for the library there are no voices)
                flatScore2.extend(list(measure.getElementsByClass('GeneralNote')))
            else:  # there are multiple voices (or an array with just one voice)
                for voice in measure.voices:
                    flatScore2.extend(list(voice.getElementsByClass('GeneralNote')))
    print("Flat score1:")
    print(flatScore1)
    print("--------------------------")
    print("Flat score2:")
    print(flatScore2)

    # compute the distance
    out = iterative_levenshtein(flatScore1, flatScore2, eq=music_eq, verbosity=3)
    return out

def midi_distance(midi1, midi2, consider_rests= True):
    """
        Midi edite distance
    """
    #flatten the midi to a list
    flatMidi1 = flat_midi(midi1, consider_rests)
    flatMidi2 = flat_midi(midi2, consider_rests)
    
    print("Flat midi1:")
    print(flatMidi1)
    print("--------------------------")
    print("Flat midi2:")
    print(flatMidi2)

    # compute the distance
    out = iterative_levenshtein(flatMidi1, flatMidi2, verbosity=3)
    return out

def score_tree_distance(score1,score2):
    """
        Return a edite distance between the hash of the trees created by each bar in the scores. 
        The edite distance uses only insertion and deletion (not modifications)
    """
    #get the ScoreMeasuresTrees from each score
    scoreTrees1 = MonophonicScoreTrees(score1)
    scoreTrees2 = MonophonicScoreTrees(score2)
    print("Score1 MeasuresTrees")
    print([t.en_beam_list for t in scoreTrees1.measuresTrees])
    print("Score2 MeasuresTrees")
    print([t.en_beam_list for t in scoreTrees2.measuresTrees])
    out = iterative_levenshtein(scoreTrees1.measuresTrees, scoreTrees2.measuresTrees, costs=(1,1,1), verbosity=4)
    return out

def polyph_score_tree_distance(score1,score2):
    """
        Return a edite distance between the hash of the trees created by each bar in the scores. 
        The edite distance uses only insertion and deletion (not modifications)
    """
    #get the ScoreTree from each score
    scoreTrees1 = ScoreTrees(score1)
    scoreTrees2 = ScoreTrees(score2)
    total_operations = []
    total_cost = 0
    #for now we assume to have an equal number of parts
    assert(len(scoreTrees1.part_list)==len(scoreTrees2.part_list))
    number_of_parts = len(scoreTrees1.part_list)
    for part_index in range(number_of_parts):
        #we evaluate the list of voices because it make sense from music perspective
        #we hope the order is the same for now
        seq1=scoreTrees1.part_list[part_index]
        seq2=scoreTrees2.part_list[part_index]
        cost, operations = iterative_levenshtein(seq1,seq2 , costs=(1,1,1), verbosity=4) #part is a seq of measures
        ############################## to change to retrieve more than one path
        total_operations.extend(operations[0]) #just the first group for now
        #############################
        total_cost += cost        
    return total_cost, total_operations



#Take a monophonic midi and return a list of note-on, note-off events
def flat_midi(midi, consider_rests= True): 
    if len(midi.tracks) != 1:
        raise TypeError('The midi1 contains more than one track')
    events_list = []
    if consider_rests: #consider both note-on and note-off
        for msg in midi.tracks[0]:
            if msg.type == 'note_on' or msg.type == 'note_off': #ignore other messages
                events_list.append((msg.note, msg.time))
    else: #consider only note-on 
        print("Not considering rests")
        delta_time = 0
        for msg in midi.tracks[0]:
            if msg.type == 'note_on': 
                events_list.append((msg.note, delta_time + msg.time))
                delta_time = 0
            else: #for all the other message, add their time to have the correct delta
                delta_time+= msg.time
    return events_list

def evaluate_noteNode_diff(noteNode1,noteNode2):
    """
        Evaluate how much one NoteNode is similar to another.
        0 is if they are equal and 4 is the maximum dissimilarity
        In particular 3 fields are compared with different weights:
            - note pitches (a chord have multiple pitches)
            - note head (black, white, long, etc.)
            - note dots
            - note ties
        Every difference will count for 1 point of dissimilarity
    """
    if (type(noteNode1) is not NoteNode) or (type(noteNode2) is not NoteNode)  : #if we are comparing object that are not NoteNode, fail
        raise TypeError("The type of noteNode1 and noteNode2  is {} and {}, but it must be NoteNode".format(type(noteNode1), type(noteNode2)))
    else: #we are comparing two NoteNode
        diff = 0
        noteNode1_info = generalNote_info(noteNode1.note)
        noteNode2_info= generalNote_info(noteNode2.note)
        #add if the type is different (e.g. a chord and a rest)
        if noteNode1_info["type"] != noteNode2_info["type"]: 
            diff += 1
        else: #compute info about the pitch only if the type is the same
            # add for the pitches
            diff += evaluate_pitch_list_diff(noteNode1_info["pitches"], noteNode2_info["pitches"])
        #add for the notehead
        if noteNode1_info["noteHead"] != noteNode2_info["noteHead"]: #add for the notehead
            diff += 1
        #add for the dots
        diff += abs(noteNode1_info["dots"]- noteNode2_info["dots"])
        #add for the ties
        if noteNode1.is_tied != noteNode2.is_tied: #exclusive or. Add if one is tied and not the other
            ################probably to revise for chords
            diff += 1
        return diff

        
def evaluate_pitch_list_diff(pitchList1, pitchList2):
    #chords are evaluate with levenstain distance, they are already sorted diatonically
    cost= iterative_levenshtein(pitchList1, pitchList2)
    return cost 