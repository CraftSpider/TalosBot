"""
    Functions and classes for building various discord.py classes
"""

import datetime as dt
import asyncio
import sys
import typing
import discord
import discord.state as state
import discord.http as dhttp


test_state = None
callbacks = {}
generated_ids = 0


class FakeHttp(dhttp.HTTPClient):

    def __init__(self, loop=None):

        if loop is None:
            loop = asyncio.get_event_loop()

        super().__init__(connector=None, loop=loop)

    def request(self, *args, **kwargs):
        raise NotImplementedError("Operation occured that isn't captured by the tests framework")

    def send_files(self, channel_id, *, files, content=None, tts=False, embed=None, nonce=None):
        print(channel_id, files, content, tts, embed, nonce)

    def send_message(self, channel_id, content, *, tts=False, embed=None, nonce=None):
        print(channel_id, content, tts, embed, nonce)


class FakeState(state.ConnectionState):

    def __init__(self, client, user_data=None, loop=None):

        if loop is None:
            loop = asyncio.get_event_loop()

        http = FakeHttp(loop=loop)

        super().__init__(dispatch=client.dispatch, chunker=None, handlers=None, syncer=None, http=http, loop=loop)

        if user_data is None:
            user_data = {
                "username": "FakeState",
                "discriminator": "0001",
                "avatar": None,
                "id_num": make_id()
            }
        user = make_user_dict(**user_data)
        self.user = discord.ClientUser(state=self, data=user)


class MessageResponse(typing.NamedTuple):
    message: discord.Message
    kwargs: typing.Dict[str, typing.Any]


def get_state():
    if test_state is None:
        raise ValueError("Discord class factories not configured")
    return test_state


def set_callback(cb, event):
    callbacks[event] = cb


def get_callback(event):
    if callbacks.get(event) is None:
        raise ValueError("Test callback not set")
    return callbacks[event]


def make_id():
    global generated_ids
    # timestamp
    discord_epoch = str(bin(int(dt.datetime.now().timestamp() * 1000) - 1420070400000))[2:]
    discord_epoch = "0" * (42 - len(discord_epoch)) + discord_epoch
    # internal worker id
    worker = "00001"
    # internal process id
    process = "00000"
    # determine how many ids have been generated so far
    generated = str(bin(generated_ids)[2:])
    generated_ids += 1
    generated = "0" * (12 - len(generated)) + generated
    # and now finally return the ID
    return int(discord_epoch + worker + process + generated, 2)


def make_user_dict(username, discriminator, avatar, id_num):
    return {
        'username': username,
        'discriminator': discriminator,
        'avatar': avatar,
        'id': id_num
    }


def make_role_dict(name, id_num):
    return {
        'id': id_num,
        'name': name
    }


def make_member_dict(username, discriminator, nick, roles, avatar, id_num):
    return {
        'user': make_user_dict(username, discriminator, avatar, id_num),
        'nick': nick,
        'roles': roles,
        'id': id_num
    }


def make_guild(name, members=None, channels=None, roles=None, owner=False, id_num=-1):
    if id_num == -1:
        id_num = make_id()
    if roles is None:
        roles = [make_role_dict("@everyone", id_num)]
    if channels is None:
        channels = []
    if members is None:
        members = []
    else:
        map(lambda x: make_member_dict(x.name, x.discriminator, x.nick, x.roles, x.avatar, x.id), members)
    member_count = len(members) if len(members) != 0 else 1
    guild = discord.Guild(
        state=get_state(),
        data={
            'name': name,
            'roles': roles,
            'channels': channels,
            'members': members,
            'member_count': member_count,
            'id': id_num,
            'owner_id': get_state().user.id if owner else 0
        }
    )
    get_state()._add_guild(guild)
    return guild


def make_text_channel(name, guild, position=-1, id_num=-1):
    if id_num == -1:
        id_num = make_id()
    if position == -1:
        position = len(guild.channels) + 1
    channel = discord.TextChannel(
        state=get_state(),
        guild=guild,
        data={
            'id': id_num,
            'name': name,
            'position': position
        }
    )
    guild._add_channel(channel)
    return channel


def make_user(username, discriminator, avatar=None, id_num=-1):
    if id_num == -1:
        id_num = make_id()
    return discord.User(
        state=get_state(),
        data=make_user_dict(username, discriminator, avatar, id_num)
    )


def make_member(username, discriminator, guild, nick=None, roles=None, avatar=None, id_num=-1):
    if id_num == -1:
        id_num = make_id()
    if int(discriminator) < 1 or int(discriminator) > 9999:
        raise ValueError("Discriminator must be between 0001 and 9999")
    if roles is None:
        roles = []
    if nick is None:
        nick = username
    member = discord.Member(
        state=get_state(),
        guild=guild,
        data=make_member_dict(username, discriminator, nick, roles, avatar, id_num)
    )
    guild._add_member(member)
    return member


def make_message(content, author, channel, pinned=False, id_num=-1):
    if id_num == -1:
        id_num = make_id()
    author = make_user_dict(author.name, author.discriminator, author.avatar, author.id)
    return discord.Message(
        state=get_state(),
        channel=channel,
        data={
            'content': content,
            'author': author,
            'pinned': pinned,
            'id': id_num
        }
    )


async def run_all_events():
    if sys.version_info[1] >= 7:
        pending = filter(lambda x: x._coro.__name__ == "_run_event", asyncio.all_tasks())
    else:
        pending = filter(lambda x: x._coro.__name__ == "_run_event", asyncio.Task.all_tasks())
    for task in pending:
        if not (task.done() or task.cancelled()):
            await task


def configure(client):
    global test_state

    if not isinstance(client, discord.Client):
        raise TypeError("Runner client must be an instance of discord.Client")

    test_state = FakeState(client)


def main():
    print(make_id())

    d_user = make_user("Test", "0001")
    d_guild = make_guild("Test_Guild")
    d_channel = make_text_channel("Channel 1", d_guild)
    d_member = make_member("Test", "0001", d_guild)

    print(d_user, d_member, d_channel)


if __name__ == "__main__":
    main()
