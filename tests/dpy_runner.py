
import sys
import asyncio
import logging
import discord
import typing
import tests.class_factories as dfacts


class RunnerConfig(typing.NamedTuple):
    client: discord.Client
    guilds: typing.List[discord.Guild]
    channels: typing.List[discord.abc.GuildChannel]
    members: typing.List[discord.Member]


log = logging.getLogger("discord.ext.tests")
cur_config = None
sent_queue = asyncio.queues.Queue()
error_queue = asyncio.queues.Queue()


async def run_all_events():
    if sys.version_info[1] >= 7:
        pending = filter(lambda x: x._coro.__name__ == "_run_event", asyncio.all_tasks())
    else:
        pending = filter(lambda x: x._coro.__name__ == "_run_event", asyncio.Task.all_tasks())
    for task in pending:
        if not (task.done() or task.cancelled()):
            await task


def verify_message(text=None, equals=True):
    if text is None:
        equals = not equals
    try:
        message = sent_queue.get_nowait()
        if equals:
            assert message.content == text, "Didn't find expected text"
        else:
            assert message.content != text, "Found unexpected text"
    except asyncio.QueueEmpty:
        raise AssertionError("No message returned by command")


def verify_embed(embed=None, allow_text=False, equals=True):
    if embed is None:
        equals = not equals
    try:
        message = sent_queue.get_nowait()
        if not allow_text:
            assert message.content is None
        elif equals:
            assert message.embeds.get(0) == embed, "Didn't find expected embed"
        else:
            assert message.embeds.get(0) != embed, "Found unexpected embed"
    except asyncio.QueueEmpty:
        raise AssertionError("No message returned by command")


def verify_file(file=None, allow_text=False, equals=True):
    if file is None:
        equals = not equals
    try:
        message = sent_queue.get_nowait()
        if not allow_text:
            assert message.content is None
        elif equals:
            assert message.attachments.get(0) == file, "Didn't find expected file"
        else:
            assert message.attachments.get(0) != file, "Found unexpected file"
    except asyncio.QueueEmpty:
        raise AssertionError("No message returned by command")


async def empty_queue():
    await run_all_events()
    while not sent_queue.empty():
        await sent_queue.get()


async def command_callback(message):
    await sent_queue.put(message)


async def error_callback(ctx, error):
    await error_queue.put((ctx, error))


async def message(content, client=None, channel=0, member=0):
    if cur_config is None:
        log.error("Attempted to make call before runner configured")
        return

    if client is None:
        client = cur_config.client

    message = dfacts.make_message(content,
                                  cur_config.members[member],
                                  cur_config.channels[channel])

    client.dispatch("message", message)
    await run_all_events()

    if not error_queue.empty():
        err = await error_queue.get()
        raise err[1]


def configure(client, num_guilds=1, num_channels=1, num_members=1):
    global cur_config

    if not isinstance(client, discord.Client):
        raise TypeError("Runner client must be an instance of discord.Client")

    dfacts.configure(client)

    # Wrap on_error so errors will be reported
    old_error = None
    if hasattr(client, "on_command_error"):
        old_error = client.on_command_error

    async def on_command_error(ctx, error):
        if old_error:
            await old_error(ctx, error)
        await error_queue.put((ctx, error))

    on_command_error.__old__ = client.on_command_error
    client.on_command_error = on_command_error

    # Configure the factories module
    dfacts.set_callback(command_callback, "message")

    guilds = []
    for num in range(num_guilds):
        guild = dfacts.make_guild(f"Test Guild {num}")
        guilds.append(guild)

    channels = []
    members = []
    for guild in guilds:

        for num in range(num_channels):
            channel = dfacts.make_text_channel(f"Channel_{num}", guild)
            channels.append(channel)
        for num in range(num_members):
            user = dfacts.make_user("TestUser", f"{num+1:04}")
            member = dfacts.make_member(user, guild)
            members.append(member)
        dfacts.make_member(dfacts.get_state().user, guild)

    cur_config = RunnerConfig(client, guilds, channels, members)
