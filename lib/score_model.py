import numpy as np
import music21


class Score:
    """The representation of a whole score"""

    def __init__(self, name):
        """Initialize a score.

        The score is root class of a complete score model.
        Its children are the parts of the score.

        Args:
            name (string): the name of the score
            TODO : metadata
        """

        self.name = name
        self.parts = [] 
    
    def add_part(self, part):
        """Add a part to the part array"""
        # TODO : check type of part
        # TODO : check if part doesn't already exist
        self.parts.append(part)

    def get_time_sig(self):
        """Returns a list of all the time signatures found in the scores"""
        # TODO
        return
    
    def get_key_sig(self):
        """Returns a list of all the key signatures found in the scores"""
        # TODO
        return
    
    def get_part(self, part_name):
        """Return the part object corresponding to the given name"""
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
    "Class for the part node"
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
    """Class for the measure node
    If a measure contains several sequence in the self.content array,
    then it has several voices. Said voices are each specified in the 
    Sequence class, except if the part has only one voice.    
    """

    def __init__(
            self, number, score, part, 
            offset, previous=None, key=None, 
            time_sig=None,clef=None, instrument=None):
        """Initialize the measure.

        The None intialized arguments are retrieved from the previous measure.
        If the previous measure is None, then it's the first measure.

        Args:
            number (int): the position of the measure in the score
            score (Score): reference of the containing score
            part (Part): reference of the containing Part
            offset (float): offset of the measure
            previous (Measure): reference to the preceding measure. None if it's the 1st.
            key (Key): the key signature of the measure. If None, references the key from the previous measure.
            time_sig (TimeSignature): the time signature of the measure. If None, references the time sig from the previous measure.
            clef (Clef): the clef signature of the measure. If None, references the clef from the previous measure.
            instrument (Instrument): the instrument of the measure. 
        """
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

        if key == None and previous != None:
            self.key = previous.key
        else:
            self.part.add_key(self.key)

        if time_sig == None and previous != None:
            self.time_sig = previous.time_sig
        else:
            self.part.add_time_sig(self.time_sig)

        if clef == None and previous != None:
            self.clef = previous.clef
        else:
            self.part.add_clef(self.clef)
        
    def update_sequence(self, sequence):
        """Add a sequence to the content of the measure"""
        # TODO : check type of sequence
        self.content.append(sequence)

    def add_key(self, key):
        """Sets the key of the measure and adds to list of keys of the part"""
        self.key = key
        self.part.add_key(key)

    def add_time_sig(self, time_sig):
        """Sets the time signature of the measure and adds to list of time signatures of the part"""
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
    """Class representing a sequence"""

    def __init__(self, measure, notes=[], voice=None):
        """Initialize the Sequence.

        Args:
            measure (Measure): reference to the parent measure
            notes (list of music21.Note): list of music21 notes
            voice (string): the name if the voice
        """
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
    """Class for an instrument.
    The object can be intialized manually, or from a music21 instrument object.
    """
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
    """Class for a clef.
    The object can be intialized manually, or from a music21.Clef object.
    """
    def __init__(self, name=None):
        self.name = name
        # TODO : Add the offset

    def from_m21(self, clef):
        if not clef: return None
        if type(clef) != music21.clef.TrebleClef: # TODO
            raise TypeError("Not a clef")
        
        self.name = clef.name

        return self

    def print(self):
        print("Clef : ", self.name)


class Key:
    """Class for an key signature.
    The object can be intialized manually, or from a music21.Key or a music21.KeySignature object.
    """

    def __init__(self, tonic=None, mode=None, offset=None):
        """
        Intialize the key

        Args:
            tonic (string): the name of the tonic 
            mode (string): the mode of the key (ex: 'major', 'minor'...)
            offset (float): the offset where the key began
        """
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
    """Class for the time signature
    The object can be intialized manually, or from a music21.meter.TimeSignature object.
    """

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