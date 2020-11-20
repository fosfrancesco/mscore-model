# %%
import numpy as np
from fractions import Fraction
from lib.music_sequences import *

seq = [0, Fraction(0.25)]
output = musical_split(seq, 3)
print(output)
expected_output = [[0, 0.75], [0], [0]]
for o, exp_o in zip(output, expected_output):
    print(np.array_equal(o, exp_o))


# %%
Fraction(0.1).limit_denominator()
