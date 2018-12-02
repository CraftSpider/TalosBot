"""
    Functions and classes for building various discord.py classes
"""

import datetime as dt
import asyncio
import sys
import discord
import discord.ext.commands as commands


test_state = None
generated_ids = 0


class FakeState:

    def __init__(self, user=None):
        if user is None:
            user = make_user_dict("State", "0000", None, make_id())
        self._users = {}
        self._guilds = {}
        self._voice_clients = {}
        self.user = discord.ClientUser(state=self, data=user)
        self._private_channels_by_user = {}
        self.shard_count = None

    @property
    def self_id(self):
        u = self.user
        return u.id if u else None

    @property
    def guilds(self):
        return list(self._guilds.values())

    @property
    def voice_clients(self):
        return list(self._voice_clients.values())

    def store_user(self, data):
        # this way is 300% faster than `dict.setdefault`.
        user_id = int(data['id'])
        try:
            return self._users[user_id]
        except KeyError:
            self._users[user_id] = user = discord.User(state=self, data=data)
            return user

    def get_user(self, uid):
        return self._users.get(uid)

    def _get_private_channel_by_user(self, user_id):
        return self._private_channels_by_user.get(user_id)

    def _add_guild(self, guild):
        self._guilds[guild.id] = guild

    def parse_user_update(self, data):
        self.user = discord.ClientUser(state=self, data=data)


class FakeContext(commands.Context):

    def __init__(self, **attrs):
        self.callback = attrs.get('callback', None)
        super().__init__(**attrs)

    def set_callback(self, callback):
        self.callback = callback

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
        value = self.callback(content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after,
                              nonce=nonce)
        if asyncio.iscoroutine(value) or asyncio.isfuture(value):
            return await value
        else:
            return value


class MessageResponse:

    __slots__ = ("message", "kwargs")

    def __init__(self, message, kwargs):
        self.message = message
        self.kwargs = kwargs


def get_state():
    global test_state
    if test_state is None:
        test_state = FakeState()
    return test_state


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
    author = make_member_dict(author.name, author.discriminator, author.nick, author.roles, author.avatar, author.id)
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


async def make_context(bot, message, callback):
    # Get the context as the bot wants
    ctx = await bot.get_context(message, cls=FakeContext)

    # Make sure that the command calls back
    ctx.callback = callback
    if ctx.command is not None:

        def make_handler(old_error):
            async def new_error(n_ctx, error):
                try:
                    await old_error(n_ctx, error)
                    await run_all_events()
                except Exception as e:
                    print(e)
                raise error
            new_error.new = True
            return new_error

        old_handler = ctx.command.dispatch_error
        if getattr(old_handler, "new", None) is None:
            ctx.command.dispatch_error = make_handler(old_handler)

        if isinstance(ctx.command, commands.Group):
            for command in ctx.command.commands:
                old_handler = command.dispatch_error
                if getattr(old_handler, "new", None) is None:
                    command.dispatch_error = make_handler(old_handler)
    return ctx


def main():
    print(make_id())

    d_user = make_user("Test", "0001")

    d_guild = make_guild("Test_Guild")

    d_channel = make_text_channel("Channel 1", d_guild)

    d_member = make_member("Test", "0001", d_guild)

    print(d_user, d_member, d_channel)


if __name__ == "__main__":
    main()
