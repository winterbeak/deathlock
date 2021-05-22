import random

import sound


NONE = 0
SOFT = 1
MEDIUM = 2
BRIGHT = 3
FULL = 4

shade_color = [(0, 0, 0), (25, 25, 25), (50, 50, 50), (100, 100, 100), (255, 255, 255)]

_OUTLINE_SOFT_PHASE = 35
_OUTLINE_MEDIUM_PHASE = 60
MAX_OUTLINE_LENGTH = 70


def _outline_length(outline):
    acc = 0
    for section in outline:
        acc += section[1]
    return acc


def _random_sequence_outline():
    outline = [(NONE, random.randint(1, 10))]

    while _outline_length(outline) < _OUTLINE_SOFT_PHASE:
        brightness = random.randint(SOFT, MEDIUM)
        if brightness == outline[-1][0]:
            continue
        if brightness == BRIGHT:
            length = random.randint(2, 3)
        elif brightness == MEDIUM:
            length = random.randint(2, 5)
        else:
            length = random.randint(8, 25)
        outline.append((brightness, length))

    while _outline_length(outline) < _OUTLINE_MEDIUM_PHASE:
        brightness = random.randint(SOFT, BRIGHT)
        length = random.randint(2, 4)
        outline.append((brightness, length))

    while _outline_length(outline) < MAX_OUTLINE_LENGTH:
        brightness = random.randint(MEDIUM, FULL)
        if brightness == FULL:
            length = random.randint(2, 15)
        else:
            length = random.randint(2, 4)
        outline.append((brightness, length))

    diff = _outline_length(outline) - MAX_OUTLINE_LENGTH
    outline[-1] = (outline[-1][0], outline[-1][1] - diff)
    return outline


def _make_sequence_list(sequence_outline):
    sequence_list = []
    for unit in sequence_outline:
        for _ in range(unit[1]):
            sequence_list.append(unit[0])
    return sequence_list


class FlickerSequence:
    _SEQUENCE_OUTLINES = [_random_sequence_outline() for _ in range(20)]
    _SEQUENCE_LISTS = [_make_sequence_list(seq) for seq in _SEQUENCE_OUTLINES]
    SEQUENCE_LENGTH = len(_SEQUENCE_LISTS[0])

    def __init__(self):
        self.sequence_list = random.choice(self._SEQUENCE_LISTS)

    def brightness(self, frame):
        if frame < 0:
            return NONE
        if frame >= len(self.sequence_list):
            return FULL
        return self.sequence_list[frame]


START_DELAY = 20
END_DELAY = 20
STOP_FLICKERING_FRAME = START_DELAY + FlickerSequence.SEQUENCE_LENGTH
TOTAL_LENGTH = START_DELAY + FlickerSequence.SEQUENCE_LENGTH + END_DELAY

SOUND_COUNT = 6
turn_on_sounds = [sound.load("flicker_on") for _ in range(SOUND_COUNT)]


def mute_sounds():
    for turn_on_sound in turn_on_sounds:
        turn_on_sound.set_volume(0)


def play_sounds():
    for turn_on_sound in turn_on_sounds:
        turn_on_sound.play()


def set_sound_volume(sound_num, brightness, mult):
    if brightness == SOFT:
        turn_on_sounds[sound_num].set_volume(0.02 * mult)
    elif brightness == MEDIUM:
        turn_on_sounds[sound_num].set_volume(0.05 * mult)
    elif brightness == BRIGHT:
        turn_on_sounds[sound_num].set_volume(0.1 * mult)
    else:
        turn_on_sounds[sound_num].set_volume(0)


mute_sounds()
