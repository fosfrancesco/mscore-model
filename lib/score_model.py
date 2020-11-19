import numpy as np
import music21


class Score:
    """The representation of a whole score"""

    def __init__(self, name):
        """Initialize a score.

        Commentaire

        Args:
        """

        self.name = name
        self.parts = [] 
    
    def add_part(self, part):
        # TODO : check if part doesn't already exist
        self.parts.append(part)

    def get_time_sig(self):
        return
    
    def get_key_sig(self):
        return
    
    def get_part(self, part_name):
        for part in self.parts:
            if part.name == part_name:
                return part
        return None

    def nb_parts(self):
        return len(self.parts)

    def nb_voices(self):
        tmp = 0
        for part in self.parts:
            max = max(tmp, part.nb_voices())
        return max

    def nb_measures(self):
        return self.parts[0].nb_measures()

    def print(self):
        # TODO
        print('score model - name : ', self.name)
        for part in self.parts:
            part.print()


class Part:
    def __init__(self, name, score, prev_part=None):
        self.name = name
        self.score = score
        self.prev_part = prev_part
        self.measures = []
        self.keys = []
        self.time_sigs = []

    def add_measure(self, measure):
        self.measures.append(measure)

    def add_key(self, key):
        self.keys.append(key)
    
    def add_time_sig(self, time_sig):
        self.time_sigs.append(time_sig)

    def nb_voices(self, measures):
        if len(measures) == 1:
            return measures.nb_voices
        else:
            return max(measures[0].nb_voices, self.nb_voices(measures[1:]))

    def print(self):
        print('  part name : ', self.name)

        for key in self.keys:
            key.print()

        for time_sig in self.time_sigs:
            time_sig.print()
        
        for measure in self.measures:
            measure.print()    
        


class Measure:
    def __init__(
            self, number, score, part, 
            offset, previous=None, key=None, 
            time_sig=None,clef=None, instrument=None):
        self.number = number
        self.score = score
        self.part = part
        self.offset = offset
        self.previous = previous
        self.key = key
        self.time_sig = time_sig
        self.clef = clef
        self.instrument = instrument

        self.content = []

        if time_sig == None and previous != None:
            self.time_sig = previous.time_sig
        else:
            self.part.add_time_sig(self.time_sig)
        
        if key == None and previous != None:
            self.key = previous.key
        else:
            self.part.add_key(self.key)

    def update_sequence(self, sequence):
        self.content.append(sequence)

    def add_key(self, key):
        self.key = key
        self.part.add_key(key)

    def add_time_sig(self, time_sig):
        self.time_sig = time_sig
        self.part.add_time_sig(self.offset, time_sig)

    def nb_voices(self):
        return len(self.content)

    def print(self):
        print('    measure', self.number, self.offset, sep=" --- ")
        # self.key.print() if self.key else None
        # self.time_sig.print() if self.time_sig else None
        # self.clef.print() if self.clef else None
        # self.instrument.print() if self.instrument else None
        for sequence in self.content:
            sequence.print()


class Sequence:
    def __init__(self, measure, notes=[], voice=None):
        self.notes = notes
        self.voice = voice
        self.measure = measure

    def add_notes(self, note):
        self.notes.append(note)

    def print(self):
        if self.voice: print('        voice : ', self.voice)
        for note in self.notes:
            print('           ',note, note.offset)



class Instrument:
    def __init__(self, name=None):
        self.name = name

    def from_m21(self, instrument):
        if not instrument: return None
        if type(instrument) != music21.instrument.Instrument:
            raise TypeError("Not an instrument")
        self.name = instrument.instrumentName

        return self

    def print(self):
        print("Instrument : ", self.name)


class Clef:
    def __init__(self, name=None):
        self.name = name

    def from_m21(self, clef):
        if not clef: return None
        if type(clef) != music21.clef.TrebleClef: # TODO
            raise TypeError("Not a clef")
        
        self.name = clef.name

        return self


    def print(self):
        print("Clef : ", self.name)


class Key:
    def __init__(self, tonic=None, mode=None, offset=None):
        self.tonic = tonic
        self.mode = mode
        self.offset = offset

    def from_m21(self, key):
        if not key: return None
        if type(key) == music21.key.KeySignature:
            key = key.asKey()
        if type(key) != music21.key.Key: # TODO
            raise TypeError("Not a key", key)
        self.tonic = key.tonic.name
        self.mode = key.mode

        return self

    def print(self):
        print('      key of ', self.tonic, self.mode, self.offset)


class TimeSignature:
    def __init__(self, numerator=None, denominator=None, offset=None):
        self.numerator = numerator
        self.denominator = denominator
        self.offset = offset

    def from_m21(self, time_sig):
        if not time_sig: return None

        if type(time_sig) != music21.meter.TimeSignature:
            raise TypeError("Not a time signature")
        self.numerator = time_sig.numerator
        self.denominator = time_sig.denominator

        return self

    def print(self):
        print('time signature : ', self.numerator, '/', self.denominator)