
import enum


class Instruction(enum.IntEnum):
    RAW: int = enum.auto()
    IF: int = enum.auto()
    ELIF: int = enum.auto()
    ELSE: int = enum.auto()
    EXEC: int = enum.auto()
