import math

""" File with constants for voice separation """

MAX_VOICES = 2

# VERTICAL COSTS
VOICE_CROSSING_COST = 100
DIFFERENT_LENGTH_COST = math.inf
#TONAL_FUSION_COST = 2  # TODO
CHORD_WIDTH_COST = math.inf

# HORIZONTAL COSTS
REST_COST = 500
OVERLAP_COST = 500
DURATION_COST = math.inf

# OTHER COSTS
NEW_VOICE_COST = 100
EMPTY_VOICE_COST = 0



