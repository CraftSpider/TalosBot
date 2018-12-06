
import asyncio
import logging
import discord
import typing
import tests.class_factories as dfacts


class RunnerConfig(typing.NamedTuple):
    client: discord.Client
    guilds: typing.Dict[str, discord.Guild]
    channels: typing.Dict[str, discord.abc.GuildChannel]
    members: typing.Dict[str, discord.Member]


log = logging.getLogger("discord.ext.tests")
cur_config = None
sent_queue = asyncio.queues.Queue()
error_queue = asyncio.queues.Queue()


def verify_message(text=None, equals=True):
    if text is None:
        equals = not equals
    try:
        response = sent_queue.get_nowait()
        if equals:
            assert response.message == text, "Didn't find expected text"
        else:
            assert response.message != text, "Found unexpected text"
    except asyncio.QueueEmpty:
        raise AssertionError("No message returned by command")


def verify_embed(embed=None, allow_text=False, equals=True):
    if embed is None:
        equals = not equals
    try:
        response = sent_queue.get_nowait()
        if not allow_text:
            assert response.message is None
        elif equals:
            assert response.kwargs["embed"] == embed, "Didn't find expected embed"
        else:
            assert response.kwargs["embed"] != embed, "Found unexpected embed"
    except asyncio.QueueEmpty:
        raise AssertionError("No message returned by command")


def verify_file(file=None, allow_text=False, equals=True):
    if file is None:
        equals = not equals
    try:
        response = sent_queue.get_nowait()
        if not allow_text:
            assert response.message is None
        elif equals:
            assert response.kwargs["file"] == file, "Didn't find expected file"
        else:
            assert response.kwargs["file"] != file, "Found unexpected file"
    except asyncio.QueueEmpty:
        raise AssertionError("No message returned by command")


async def empty_queue():
    while not sent_queue.empty():
        await sent_queue.get()


async def command_callback(content, **kwargs):
    response = dfacts.MessageResponse(content, kwargs)
    await sent_queue.put(response)


async def error_callback(ctx, error):
    await error_queue.put((ctx, error))


async def call(content, client=None, channel=1, member="member_1"):
    if cur_config is None:
        log.error("Attempted to make call before runner configured")
        return

    if client is None:
        client = cur_config.client

    message = dfacts.make_message(content,
                                  cur_config.members[member],
                                  cur_config.channels[f"channel_{channel}"])

    client.dispatch("message", message)
    await dfacts.run_all_events()

    if not error_queue.empty():
        err = await error_queue.get()
        raise err[1]


def configure(client, guilds, channels, members):
    global cur_config

    if not isinstance(client, discord.Client):
        raise TypeError("Runner client must be an instance of discord.Client")

    # Wrap on_error so errors will be reported
    @staticmethod
    async def on_command_error(ctx, error):
        if hasattr(client, "on_command_error"):
            await client.on_command_error(ctx, error)
        await error_queue.put((ctx, error))
    on_command_error.__old__ = client.on_command_error
    client.on_command_error = on_command_error

    dfacts.set_callback(command_callback, "message")

    # TODO: generate desired guilds, channels, and members

    cur_config = RunnerConfig(client, guilds, channels, members)
