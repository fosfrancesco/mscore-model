# %%
import numpy as np
from fractions import Fraction
from lib.music_sequences import *
from lib.bar_trees import *

root = Root()
sequence_to_rhythm_tree(
    np.array([Fraction(0), Fraction(1, 6), Fraction(1, 2), Fraction(7, 8)]), 0, root
)
t = Tree(root)
t.show()


# %%
Fraction(0.1).limit_denominator()

# %%
