"""
    twitch_irc client stub file
"""

from typing import Any, Union, List, Dict, Tuple
import logging
import irc.client
import irc.bot
import abc

log = ... # type: logging.Logger

class Messageable(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def send(self, message: Any) -> None: ...

class TwitchReactor(irc.client.Reactor):

    def __init__(self) -> None: ...

    def server(self) -> TwitchConnection: ...

class TwitchConnection(irc.client.ServerConnection):

    socket = ... # type:

    def __init__(self, reactor: TwitchReactor) -> None: ...

    def __str__(self) -> str: ...

    def _handle_event(self, event: irc.client.Event) -> None: ...

    def req_membership(self) -> None: ...

    def req_tags(self) -> None: ...

    def req_commands(self) -> None: ...

    def clearchat(self, channel: Union[TwitchChannel, str], user: str, duration: int = ..., reason: str = ...) -> None: ...

    action: None
    admin: None
    ctcp: None
    ctcp_reply: None
    globops: None
    info: None
    invite:  None
    ison:  None
    kick:  None
    links:  None
    list:  None
    lusers:  None
    motd:  None
    names:  None
    notice:  None
    oper:  None
    squit:  None
    stats:  None
    time:  None
    topic:  None
    trace:  None
    userhost:  None
    users:  None
    version:  None
    wallops:  None
    who:  None
    whois:  None
    whowas:  None

class TwitchChannel(irc.bot.Channel, Messageable):

    __slots__ = ... # type: str

    name = ... # type: str
    server = ... # type: TwitchConnection

    def __init__(self, conn: TwitchConnection, name: str) -> None: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def send(self, message: Any) -> None: ...

class MessageTags:

    badges: str
    color: str
    display_name: str
    emotes: str
    id: int
    mod: bool
    room_id: int
    subscriber: bool
    tmi_sent_ts: int
    turbo: bool
    user_id: int
    user_type: str

    def __init__(self, user_tags: List[Dict[str, str]]) -> None: ...

