
import enum


class Instruction(enum.IntEnum):
    RAW = 0

    IF = 1
    ELIF = 2
    ELSE = 3

    EXEC = 4
