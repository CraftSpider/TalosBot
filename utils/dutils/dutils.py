"""
    Various discord specific helper methods and variables

    Author: CraftSpider
"""

import discord
import discord.ext.commands as commands
import functools
import re

# Useful Variables

mention_patterns = {
    "user": re.compile(r"<@!?\d+>"),
    "channel": re.compile(r"<#\d+>"),
    "role": re.compile(r"<@​&\d+>")
}


# Checks


def admin_local(self, ctx):
    """
        Determine whether the person calling the command is an admin or dev.
    :param self: The cog this check is attached to
    :param ctx: The context being checked
    :return: Boolean, whether the user has admin or dev perms
    """
    if isinstance(ctx.channel, discord.abc.PrivateChannel):
        return True
    command = str(ctx.command)

    if dev_local(self, ctx):
        return True

    admins = ctx.bot.database.get_admins(ctx.guild.id)
    if len(admins) == 0 and ctx.author.guild_permissions.administrator or\
       ctx.author == ctx.guild.owner or\
       next((x for x in admins if x.user_id == ctx.author.id), None) is not None:
        return True

    perms = ctx.bot.database.get_perm_rules(ctx.guild.id, command)
    if len(perms) == 0:
        return False
    perms.sort()
    for perm in perms:
        result = perm.get_allowed(ctx)
        if result is None:
            continue
        return result
    return False


def dev_local(self, ctx):
    """
        Determine whether the person calling the command is a dev.
    :param self: The cog this check is attached to
    :param ctx: The context being checked
    :return: Boolean, whether the user has dev permissions
    """
    return ctx.author.id in ctx.bot.DEVS


def admin_check():
    """
        Decorator for adding admin check to a single command
    :return: Command check
    """
    return commands.check(functools.partial(admin_local, None))


def dev_check():
    """
        Decorator for adding dev check to a single command
    :return: Command check
    """
    return commands.check(functools.partial(dev_local, None))


# Helper utils


def is_mention(text):
    """
        Check whether a piece of text is any kind of discord mention
    :param text: Text to check
    :return: Whether text is a mention
    """
    for pattern in mention_patterns:
        if mention_patterns[pattern].match(text):
            return True
    return False


def is_user_mention(text):
    """
        Check if a piece of text is a discord user mention
    :param text: Text to check
    :return: Whether text is a user mention
    """
    return mention_patterns["user"].match(text) is not None


def is_role_mention(text):
    """
        Check if a piece of text is a discord role mention
    :param text: Text to check
    :return: Whether text is a role mention
    """
    return mention_patterns["role"].match(text) is not None


def is_channel_mention(text):
    """
        Check if a piece of text is a discord channel mention
    :param text: Text to check
    :return: Whether text is a channel mention
    """
    return mention_patterns["channel"].match(text) is not None


def get_id(mention):
    """
        Get the ID out of a mention as a string
    :param mention: String of just the mention
    :return: Snowflake ID as an int
    """
    return int(mention.strip("<@#&!>"))


async def _send_paginated(self, msg, prefix="```", suffix="```"):
    """
        Send a message in a paginated form automatically. Does a naive split, breaking every maximum number of
        characters with no respect for newlines. Actually attached to the Context class dynamically
    :param self: Context object
    :param msg: Message to send
    :param prefix: Prefix for the paginator on each page
    :param suffix: Suffix for the paginator on each page
    """
    msg = str(msg)
    pag = commands.Paginator(prefix=prefix, suffix=suffix)

    for line in [msg[i:i+pag.max_size-len(prefix+suffix)] for i in range(0, len(msg), pag.max_size-len(prefix+suffix))]:
        pag.add_line(line.strip())
    for page in pag.pages:
        await self.send(page)
commands.Context.send_paginated = _send_paginated
