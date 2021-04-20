import music21 as m21 
# accurracy calculated inspired by : VOISE: LEARNING TO SEGREGATE VOICESIN EXPLICIT AND IMPLICIT POLYPHONY (Phillip B. KirlinandPaul E. Utgof)

# vertical : return true if the two simultaneous notes are in the same voice
def are_in_same_voice(score, note1, note2):
    for part in score.parts:
        if part.hasElement(note1) and part.hasElement(note2):
            return 1
    return 0

# horizontal
def soundness(score, note1, note2):
    for part in score.parts:
        if part.hasElement(note1) and part.hasElement(note2):
            return True
    return False

# get voices from a score as a list of streams
def get_voices(score):
    new_stream = m21.stream.Score()
    s = score.voicesToParts()
    i = 1
    for part in s.parts:
        new_stream.insert(part.flat)
        part.id = i
        i = i + 1
    return new_stream

