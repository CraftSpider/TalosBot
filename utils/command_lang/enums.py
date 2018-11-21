
import enum


class Instruction(enum.IntEnum):
    """
        Instructions supported by CommandLang. Instruction opcodes, essentially
        Existing codes should stay the same when possible, new instructions get new opcodes
    """
    RAW = 0

    IF = 1
    ELIF = 2
    ELSE = 3

    EXEC = 4
