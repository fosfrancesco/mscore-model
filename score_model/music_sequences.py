from typing import List
import numpy as np
from fractions import Fraction
from .constant import CONTINUATION_SYMBOL, REST_SYMBOL
import numbers
import pretty_midi as pm


class Event:
    def __init__(self, timestamp, musical_artifact):
        self.timestamp = timestamp
        self.musical_artifact = musical_artifact

    def __add__(self, number: numbers.Number):
        return Event(self.timestamp + number, self.musical_artifact)

    def __sub__(self, number: numbers.Number):
        return Event(self.timestamp - number, self.musical_artifact)

    def __mul__(self, number: numbers.Number):
        return Event(self.timestamp * number, self.musical_artifact)

    def __truediv__(self, number: numbers.Number):
        return Event(self.timestamp / number, self.musical_artifact)

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __eq__(self, other):
        return (self.timestamp, self.musical_artifact) == other

    def __str__(self):
        return str((self.timestamp, self.musical_artifact))

    def __repr__(self):
        return str((self.timestamp, self.musical_artifact))


class Timeline:
    def __init__(
        self, events, start=0, end=1, auto_sort=False,
    ):
        if auto_sort:  # sort if requested
            events = sorted(events)
        if (
            len(events) == 0 or events[0].timestamp != start
        ):  # if the first event does not happen on start
            # add a continuation at the beginning
            events = np.concatenate(([Event(start, CONTINUATION_SYMBOL)], events))
        self.events = np.array(events)
        self.start = start
        self.end = end

    def get_timestamps(self):
        return [e.timestamp for e in self.events]

    def get_musical_artifacts(self):
        return [e.musical_artifact for e in self.events]

    def __len__(self):
        return len(self.events)

    def __repr__(self):
        return "Tim{},[{},{}[".format(self.events, self.start, self.end)

    def __eq__(self, other):
        if not isinstance(other, Timeline):
            return False
        else:
            return (
                np.array_equal(self.events, other.events)
                and self.start == other.start
                and self.end == other.end
            )

    def __add__(self, other):
        shifted_other = other.shift_and_rescale(new_start=self.end)
        return Timeline(
            np.concatenate([self.events, shifted_other.events]),
            start=self.start,
            end=shifted_other.end,
        )

    def split(self, k: int, normalize: bool = False):
        # compute the split points
        split_points = [
            Fraction(i, k) * Fraction((self.end - self.start)) + Fraction(self.start)
            for i in range(0, k + 1)
        ]
        # compute the indices where we need to split
        split_indices = [
            np.searchsorted(self.get_timestamps(), s) for s in split_points
        ]
        # split the events according to those indices (and normalize if required)
        return [
            Timeline(
                (self.events[ind[0] : ind[1]] - split_points[i]) * k + self.start,
                start=self.start,
                end=self.end,
            )
            if normalize
            else Timeline(
                self.events[ind[0] : ind[1]],
                start=split_points[i],
                end=split_points[i + 1],
            )
            for i, ind in enumerate(zip(split_indices[:-1], split_indices[1:]))
        ]

    def shift_and_rescale(self, new_start=None, new_end=None):
        # if new_start and new end are not provided, default to 0 and 1
        if new_start is None and new_end is None:
            new_start = 1
            new_end = 1
        # if only new start is provided, we set new_end to keep the same lenght
        elif (not new_start is None) and new_end is None:
            new_end = new_start + (self.end - self.start)
        # if they are both provided, pass
        elif (not new_start is None) and (not new_end is None):
            pass
        # if only new end is defined, exception
        else:
            raise Exception("you must define new_end if you define new_start")
        return Timeline(
            (self.events - self.start)
            * Fraction(new_end - new_start, self.end - self.start)
            + new_start,
            start=new_start,
            end=new_end,
        )

    def to_json(self, time_type: str) -> List[dict]:
        """Generates a list of dictionaries representation of a timeline. One dict for each event.

        Args:
            time_type (str): either "onset"or "duration"

        Raises:
            TypeError: if time_type is invalid

        Returns:
            list(dict): A list of dictionaries describing the events in the timeline.
        """
        event_list = []
        if time_type == "onset":
            for event in self.events:
                musical_artif = (  # to avoid the numpy array for the json encoding
                    event.musical_artifact
                    if event.musical_artifact == REST_SYMBOL
                    else list(event.musical_artifact)
                )
                event_list.append(
                    {
                        "onset": {
                            "numerator": int(Fraction(event.timestamp).numerator),
                            "denominator": int(Fraction(event.timestamp).denominator),
                        },
                        "musical_artifact": musical_artif,
                    }
                )
            return event_list
        if time_type == "duration":
            onsets = [e.timestamp for e in self.events]
            durations = [of - on for on, of in zip(onsets, onsets[1:] + [self.end])]
            for ie, event in enumerate(self.events):
                musical_artif = (  # to avoid the numpy array for the json encoding
                    event.musical_artifact
                    if event.musical_artifact == REST_SYMBOL
                    else list(event.musical_artifact)
                )
                event_list.append(
                    {
                        "duration": {
                            "numerator": int(Fraction(durations[ie]).numerator),
                            "denominator": int(Fraction(durations[ie]).denominator),
                        },
                        "musical_artifact": musical_artif,
                    }
                )
            return event_list
        else:
            raise TypeError(
                time_type,
                "is not a valid type. time_type must be either 'onset' or 'duration'",
            )


def split_content(seq, k: int, interval=(0, 1)):
    """Split the content of a sorted array in equal intervals.

    For an interval (a,b) it will split at positions [Fraction(i, k) * a + b) for i in range(1, k)].
    For example for the interval (0,2) with k=4, it will split at 0.5,1,1.5.
    WARNING: the sequence should contains Fraction with limit_denominator to avoid rounding problems.
    Also problematic fractions like 0.1 could create problems

    Args:
        seq (list): the input list of numbers
        k (int): the number of intervals

    Returns:
        list: A list of intervals
    """
    # compute the indices where we need to split
    split_indices = [
        np.searchsorted(
            seq,
            Fraction(i, k) * Fraction((interval[1] - interval[0]))
            + Fraction(interval[0]),
        )
        for i in range(1, k)
    ]
    # split according to the indices
    return np.split(seq, split_indices)


def musical_split(seq, k: int):
    """Split a sequence of musical events in the interval [0,1[ in subsequences and rescale them.

    This function add the beginning of the interval. 
    For example music splitting the sequence [0,0.25,0.75] in 2 parts generates two arrays [0,0.5], [0,0.5]

    Args:
        seq (list): the input list of temporal postion of musical events
        k (int): the number of intervals
    """
    borders = [Fraction(i, k) for i in range(0, k + 1)]
    return [
        (np.concatenate(([b], o)) - b) * Fraction(k)
        if (o.size == 0 or o[0] != b)
        else (o - b) * Fraction(k)
        for b, o in zip(borders[:-1], split_content(seq, k, (0, 1)))
    ]


class MusicalContent:
    def __init__(self, timelines: List[Timeline]):
        self.timelines = timelines

    def to_json(self, time_type: str) -> dict:
        return {"voices": [t.to_json(time_type) for t in self.timelines]}

