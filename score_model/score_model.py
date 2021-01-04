import copy


class ScoreModel:
    """Class that represent a score
    """

    def __init__(self, m21_score, auto_format=True, produce_trees=False):
        """Initialize the ScoreModel from a music21 score object

        Args:
            m21_score (music21.stream.Score): the music21 score to import
            auto_format (bool, optional): Auto format the score with the hierarchy score, parts, measures, voices. Defaults to True.
            produce_trees (bool, optional): Produce the BT and TT for each measure. Defaults to False.
        """
        score = copy.deepcopy(m21_score)
        # to complete...

