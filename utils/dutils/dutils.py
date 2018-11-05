"""
    Various discord specific helper methods and variables

    Author: CraftSpider
"""

import discord
import re

# Useful Variables

mention_patterns = {
    "user": re.compile("<@!?\d+>"),
    "channel": re.compile("<#\d+>"),
    "role": re.compile("<@​&\d+>")
}


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
