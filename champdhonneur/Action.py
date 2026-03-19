from enum import Enum

class Action(Enum):
    FORCE_PASS = 0
    PASS = 1
    RECRUIT = 2
    SUMMON = 3
    MOVE = 4
    ATTACK = 5
    STACK = 6
    CAPTURE = 7