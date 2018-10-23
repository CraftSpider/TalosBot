"""
    Talos utils stub file
"""

from typing import Dict
import discord.ext.commands as dcommands


fullwidth_transform: Dict[str, str] = ...
tz_map: Dict[str, float] = ...

def to_snake_case(text: str) -> str: ...

def to_camel_case(text: str, upper: bool = ...) -> str: ...

def zero_pad(text: str, length: int) -> str: ...
