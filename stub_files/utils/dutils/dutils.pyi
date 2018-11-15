
from discord_talos.talos import Talos
from typing import Dict, Pattern
import discord.ext.commands as commands


mention_patterns: Dict[str, Pattern]


def admin_local(self: Talos, ctx: commands.Context) -> bool: ...


def is_mention(text: str) -> bool: ...

def is_user_mention(text: str) -> bool: ...

def is_role_mention(text: str) -> bool: ...

def is_channel_mention(text: str) -> bool: ...

def get_id(mention: str) -> int: ...
