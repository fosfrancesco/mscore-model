# Problems
- **too slow** : should calculate less configurations. We could sort the notes, and only take configs where adjacent notes are permutated. That would save time from processing configs that don't make sense at all, even if voice crossings are allowed (for example : notes sorted in reverse)

- when applied to one measure, the algorithm doesn't take into account if the note can be added without exceeding the measure