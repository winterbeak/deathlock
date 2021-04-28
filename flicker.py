import random


NONE = 0
SOFT = 1
MEDIUM = 2
BRIGHT = 3
FULL = 4


def _make_sequence_list(sequence_outline):
    sequence_list = []
    for unit in sequence_outline:
        for _ in range(unit[1]):
            sequence_list.append(unit[0])
    return sequence_list


class FlickerSequence:
    _SEQUENCE_OUTLINES = [
        [(NONE, 2), (MEDIUM, 2), (SOFT, 8), (BRIGHT, 2), (SOFT, 18), (MEDIUM, 2), (FULL, 2)],
        [(NONE, 4), (BRIGHT, 2), (MEDIUM, 10), (SOFT, 2), (MEDIUM, 6), (BRIGHT, 2), (FULL, 10)],
        [(NONE, 16), (MEDIUM, 4), (SOFT, 2), (BRIGHT, 2), (MEDIUM, 3), (FULL, 3)],
        [(SOFT, 10), (MEDIUM, 2), (SOFT, 8), (MEDIUM, 2), (SOFT, 10), (BRIGHT, 4)],
        [(NONE, 8), (SOFT, 20), (BRIGHT, 4), (MEDIUM, 4)],
        [(NONE, 6), (MEDIUM, 4), (SOFT, 10), (BRIGHT, 11), (FULL, 5)],
        [(NONE, 12), (MEDIUM, 6), (SOFT, 4), (BRIGHT, 12), (FULL, 2)],
        [(NONE, 2), (SOFT, 8), (BRIGHT, 4), (FULL, 10), (MEDIUM, 8), (FULL, 4)]
    ]
    _SEQUENCE_LISTS = [_make_sequence_list(seq) for seq in _SEQUENCE_OUTLINES]
    SEQUENCE_LENGTH = len(_SEQUENCE_LISTS[0])

    def __init__(self):
        self._sequence_list = random.choice(self._SEQUENCE_LISTS)

    def brightness(self, frame):
        if frame < 0:
            return NONE
        if frame >= len(self._sequence_list):
            return FULL
        return self._sequence_list[frame]


START_DELAY = 40
END_DELAY = 20
STOP_FLICKERING_FRAME = START_DELAY + FlickerSequence.SEQUENCE_LENGTH
TOTAL_LENGTH = START_DELAY + FlickerSequence.SEQUENCE_LENGTH + END_DELAY
