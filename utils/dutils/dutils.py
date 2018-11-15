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
    "user": re.compile("<@!?\d+>"),
    "channel": re.compile("<#\d+>"),
    "role": re.compile("<@​&\d+>")
}


# Checks


def admin_local(self, ctx):
    """Determine whether the person calling the command is an admin or dev."""
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
    """Determine whether the person calling the command is a dev."""
    return ctx.author.id in ctx.bot.DEVS


def admin_check():
    return commands.check(functools.partial(admin_local, None))


def dev_check():
    return commands.check(functools.partial(dev_check, None))


# Helper utils


def is_mention(text):
    for pattern in mention_patterns:
        if mention_patterns[pattern].match(text):
            return True
    return False


def is_user_mention(text):
    return mention_patterns["user"].match(text) is not None


def is_role_mention(text):
    return mention_patterns["role"].match(text) is not None


def is_channel_mention(text):
    return mention_patterns["channel"].match(text) is not None


def get_id(mention):
    return int(mention.strip("<@#&!>"))
