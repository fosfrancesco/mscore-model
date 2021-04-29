import music21 as m21
import numpy as np

def compare(note1, note2):
    return note1 == note2 and note1.offset == note2.offset

# "on calcule le nombre d'opérations nécessaires pour transformer une chaine de caractères en une autre"
def voice_distance(voice1, voice2):
    x = len(voice1)
    y = len(voice2)

    # empty voice case
    if not x: return y
    if not y: return x
    
    # init matrix
    d = np.zeros((x+1, y+1))
    for i in range(x): d[i, 0] = i
    for j in range(y): d[0, j] = j

    for i in range(1, x+1):
        for j in range(1, y+1):
            sub_cost = int(not compare(voice1[i-1], voice2[j-1]))
            d[i, j] = min(
                d[i-1, j] + 1, # effacement du nveau caractère de voice1
                d[i, j-1] + 1, # insertion dans voice1 du nouveau caractère de voice2
                d[i-1, j-1] + sub_cost, # substition
            )
            if i > 1 and j > 1 and compare(voice1[i-1], voice2[j-2]) and compare(voice1[i-2], voice2[j-1]):
                d[i, j] = min(
                    d[i, j],
                    d[i-2, j-2] + sub_cost # transposition
                )
    return d[x, y]

def score_compare(stream1, stream2):
    x = len(stream1)
    y = len(stream2)

    if x != y: 
        raise Exception("Cannot compare two scores with different number of voices")

    m = np.zeros((x, y))
    for voice1, i in zip(stream1, range(x)):
        for voice2, j in zip(stream2, range(y)):
            m[i, j] = voice_distance(voice1, voice2)

    cost = 0
    for i in range(0, len(m)):
        print(m)
        min = np.amin(m[i])
        index = np.where(min == m[i])[0][0]
        if i < len(m)-1: m[i+1, index] = np.inf
        cost += min
    return cost

    
"""
voice1 = m21.stream.Voice()
voice2 = m21.stream.Voice()
voice3 = m21.stream.Voice()
voice4 = m21.stream.Voice()

voice1.append(m21.note.Note('C#4', type='half'))
voice1.append(m21.note.Note('D#4', type='half'))
voice1.append(m21.note.Note('E#4', type='half'))

voice2.append(m21.note.Note('A#4', type='half'))
voice2.append(m21.note.Note('E#4', type='half'))
voice2.append(m21.note.Note('D#4', type='half'))

voice3.append(m21.note.Note('C#4', type='half'))
voice3.append(m21.note.Note('E#4', type='half'))
voice3.append(m21.note.Note('E#4', type='half'))

voice4.append(m21.note.Note('A#4', type='half'))
voice4.append(m21.note.Note('D#4', type='half'))
voice4.append(m21.note.Note('D#4', type='half'))

score1 = m21.stream.Score()
score2 = m21.stream.Score()

score1.append(voice1)
score1.append(voice2)

score2.append(voice3)
score2.append(voice4)

print(score_compare(score1, score2))
print(score_compare(score1, score1))


"""
