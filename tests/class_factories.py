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

        self.state = None

        super().__init__(connector=None, loop=loop)

    def generate_response(self):
        pass

    async def request(self, *args, **kwargs):
        raise NotImplementedError("Operation occured that isn't captured by the tests framework")

    async def send_files(self, channel_id, *, files, content=None, tts=False, embed=None, nonce=None):
        print(channel_id, files, content, tts, embed, nonce)
        # TODO: Return data for message

    async def send_message(self, channel_id, content, *, tts=False, embed=None, nonce=None):
        frame = sys._getframe(1)
        locs = frame.f_locals
        channel = locs.get("channel", None)
        del frame

        embeds = []
        if embed:
            embeds.append(embed)
        author = self.state.user
        data = make_message_dict(
            dict_from_user(author), make_id(), content=content, tts=tts, embeds=embeds, nonce=nonce
        )

        if callbacks.get("message"):
            message = self.state.create_message(channel=channel, data=data)
            await callbacks["message"](message)

        return data


class FakeState(state.ConnectionState):

    def __init__(self, client, http, user=None, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()

        super().__init__(dispatch=client.dispatch, chunker=None, handlers=None, syncer=None, http=http, loop=loop)

        http.state = self

        if user is None:
            user = discord.ClientUser(state=self, data=make_user_dict("FakeState", "0001", None, make_id()))

        self.user = user


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
        raise ValueError(f"Callback for event {event} not set")
    return callbacks[event]


def remove_callback(event):
    return callbacks.pop(event, None)


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


def _fill_optional(data, obj, items):
    if isinstance(obj, dict):
        for item in items:
            result = obj.pop
            if result is None:
                continue
            data[item] = result
    else:
        for item in items:
            if hasattr(obj, item):
                data[item] = getattr(obj, item)


def make_user_dict(username, discrim, avatar, id_num, flags=0, **kwargs):
    if isinstance(discrim, int):
        assert 0 < discrim < 10000
        discrim = f"{discrim:04}"
    elif isinstance(discrim, str):
        assert len(discrim) == 4 and discrim.isdigit() and 0 < int(discrim) < 10000
    out = {
        'id': id_num,
        'username': username,
        'discriminator': discrim,
        'avatar': avatar,
        'flags': flags
    }
    items = ("bot", "mfa_enabled", "locale", "verified", "email", "premium_type")
    _fill_optional(out, kwargs, items)
    return out


def dict_from_user(user):
    out = {
        'id': user.id,
        'username': user.name,
        'discriminator': user.discriminator,
        'avatar': user.avatar
    }
    items = ("bot", "mfa_enabled", "locale", "verified", "email", "premium_type")
    _fill_optional(out, user, items)
    return out


def make_member_dict(user, roles, joined=0, deaf=False, mute=False, **kwargs):
    out = {
        'user': user,
        'roles': roles,
        'joined_at': joined,
        'deaf': deaf,
        'mute': mute
    }
    items = ("nick",)
    _fill_optional(out, kwargs, items)
    return out


def dict_from_member(member):
    out = {
        'user': dict_from_user(member._user),
        'roles': member.roles,
        'joined_at': member.joined_at,
        'deaf': member.deaf,
        'mute': member.mute
    }
    items = ("nick",)
    _fill_optional(out, member, items)
    return out


def make_role_dict(name, id_num, colour=0, hoist=False, position=-1, perms=0, managed=False, mentionable=False):
    return {
        'id': id_num,
        'name': name,
        'color': colour,
        'hoist': hoist,
        'position': position,
        'permissions': perms,
        'managed': managed,
        'mentionable': mentionable
    }


def dict_from_role(role):
    return {
        'id': role.id,
        'name': role.name,
        'color': role.colour,
        'hoist': role.hoist,
        'position': role.position,
        'permissions': role.permissions.value,
        'managed': role.managed,
        'mentionable': role.mentionable
    }


def make_text_channel_dict(name, position, id_num):
    return {
        'id': id_num,
        'name': name,
        'position': position
    }


def dict_from_channel(channel):
    return {
        'name': channel.name,
        'position': channel.position,
        'id': channel.id
    }


def make_message_dict(author, id_num, **kwargs):
    out = {
        'author': author,
        'id': id_num
    }
    items = ('content', 'pinned', 'application', 'activity', 'mention_everyone', 'tts', 'type', 'attachments', 'embeds',
             'nonce')
    _fill_optional(out, kwargs, items)
    return out


def message_to_dict(message):
    out = {
        'id': message.id,
        'author': dict_from_user(message.author),
    }
    items = ('content', 'pinned', 'application', 'activity', 'mention_everyone', 'tts', 'type', 'attachments', 'embeds',
             'nonce')
    _fill_optional(out, message, items)
    return out


def make_guild(name, members=None, channels=None, roles=None, owner=False, id_num=-1):
    if id_num == -1:
        id_num = make_id()
    if roles is None:
        roles = [make_role_dict("@everyone", id_num)]
    if channels is None:
        channels = []
    else:
        channels = map(lambda x: dict_from_channel(x), channels)
    if members is None:
        members = []
    else:
        members = map(lambda x: dict_from_member(x), members)
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
        data=make_text_channel_dict(name, position, id_num)
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
    if int(discriminator) < 1 or int(discriminator) > 9999:
        raise ValueError("Discriminator must be between 0001 and 9999")
    if roles is None:
        roles = []
    if nick is None:
        nick = username

    user = make_user(username, discriminator, avatar, id_num)

    member = discord.Member(
        state=get_state(),
        guild=guild,
        data=make_member_dict(user, roles, nick=nick)
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
        data=make_message_dict(author, id_num, content=content, pinned=pinned)
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

    loop = asyncio.get_event_loop()

    http = FakeHttp(loop=loop)

    client.http = http
    test_state = FakeState(client, http=http, loop=loop)

    client._connection = test_state


def main():
    print(make_id())

    d_user = make_user("Test", "0001")
    d_guild = make_guild("Test_Guild")
    d_channel = make_text_channel("Channel 1", d_guild)
    d_member = make_member("Test", "0001", d_guild)

    print(d_user, d_member, d_channel)


if __name__ == "__main__":
    main()
