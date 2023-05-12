from enum import Enum


class Judgement(Enum):
    GHOST = 0
    HIT100 = 1
    HIT300 = 2
    MISS = 3
    IDLE = 4


class Action(Enum):
    STILL = 0
    KEY_1 = 1
    KEY_2 = 2


class NoteType(Enum):
    SMALL_BLUE = 0
    SMALL_RED = 1
    LARGE_BLUE = 2
    LARGE_RED = 3


class Note:
    def __init__(self, time: int, speed: int, n_type: NoteType):
        self.time = time
        self.speed = speed
        self.type = n_type
