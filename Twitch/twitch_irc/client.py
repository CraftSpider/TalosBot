"""
    Fresh library for Twitch bots through IRC
"""

import abc
import irc.bot
import irc.features
import irc.client


class Messageable(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def send(self, message):
        pass


class TwitchReactor(irc.client.Reactor):

    def __init__(self):
        super().__init__()

    def server(self):
        c = TwitchConnection(self)
        with self.mutex:
            self.connections.append(c)
        return c


class TwitchConnection(irc.client.ServerConnection):
    """
        A Twitch IRC server connection.

        TwitchConnection objects are instantiated by calling the server
        method on a TwitchReactor object.
    """

    socket = None

    def __init__(self, reactor):
        self.set_rate_limit(20/30)
        super().__init__(reactor)

    def __str__(self):
        return "TwitchConnection(Server: {}, Port: {}, Nickname: {})".format(
            self.server, self.port, self.nickname
        )

    def req_membership(self):
        self.cap("REQ", "twitch.tv/membership")

    def req_tags(self):
        self.cap("REQ", "twitch.tv/tags")

    def req_commands(self):
        self.cap("REQ", "twitch.tv/commands")

    def clearchat(self, channel, user, duration=-1, reason=""):
        tags = "@"
        if duration >= 0:
            tags += "ban-duration={};".format(duration)
        if reason != "":
            tags += "ban-reason={};".format(reason)
        tags = "" if tags == "@" else None
        self.send_items(tags, "CLEARCHAT", channel, ":{}".format(user))

    action = None
    admin = None
    ctcp = None
    ctcp_reply = None
    globops = None
    info = None
    invite = None
    ison = None
    kick = None
    links = None
    list = None
    lusers = None
    motd = None
    names = None
    notice = None
    oper = None
    squit = None
    stats = None
    time = None
    topic = None
    trace = None
    userhost = None
    users = None
    version = None
    wallops = None
    who = None
    whois = None
    whowas = None


class TwitchChannel(irc.bot.Channel, Messageable):

    def __init__(self, conn, name):
        super().__init__()
        self.name = name
        self.server = conn

    def __str__(self):
        return "TwitchChannel(Name: {})".format(self.name)

    def __repr__(self):
        return "TwitchChannel(name=\"{}\")".format(self.name)

    def send(self, message):
        self.server.privmsg(self.name, message)
