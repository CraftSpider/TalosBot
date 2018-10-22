
import inspect
import logging
import discord
import discord.ext.commands as commands

from .events import EventLoop


log = logging.getLogger("talos.dutils.bot")


class ExtendedBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.all_events = {}

    # Extensions to super functionality

    def add_cog(self, cog):
        super().add_cog(cog)

        members = inspect.getmembers(cog)
        for name, member in members:
            if isinstance(member, EventLoop):
                member.parent = cog
                self.add_event(member)

    def remove_cog(self, name):
        cog = self.cogs.pop(name, None)
        if cog is None:
            return

        members = inspect.getmembers(cog)
        for name, member in members:
            # remove events the cog has
            if isinstance(member, EventLoop):
                self.remove_event(member.name)

        super().remove_cog(name)

    def load_extension(self, name, prefix=True):
        extdir = getattr(self, "extension_dir")
        if extdir is not None and prefix:
            name = extdir + "." + name
        super().load_extension(name)

    def unload_extension(self, name, prefix=True):
        extdir = getattr(self, "extension_dir")
        if extdir is not None and prefix:
            name = extdir + "." + name
        super().unload_extension(name)

    def run(self, token, *args, **kwargs):
        def_exts = getattr(self, "startup_extensions")
        if def_exts is not None:
            self.load_extensions(def_exts)
        for event in self.all_events:
            self.all_events[event].start()
        super().run(token, *args, **kwargs)

    # Event loop functions

    def add_event(self, event):
        if not isinstance(event, EventLoop):
            raise TypeError('The event passed must be a subclass of EventLoop')

        if event.name in self.all_events:
            raise discord.ClientException(f"Event {event.name} is already registered.")

        self.all_events[event.name] = event

    def remove_event(self, name):
        event = self.all_events.pop(name)
        if event is None:
            return None

        event.stop()
        event.parent = None

        return event

    # New helper methods

    def load_extensions(self, extensions):
        """
            Loads all extensions in input, or all Talos extensions defined in STARTUP_EXTENSIONS if array is None.
            :param extensions: extensions to load, None if all in STARTUP_EXTENSIONS
            :return: 0 if successful, 1 if unsuccessful
        """
        log.info("Loading multiple extensions")
        clean = 0
        for extension in extensions:
            try:
                log.debug(f"Loading extension {extension}")
                self.load_extension(extension)
            except Exception as err:
                clean += 1
                exc = f"{type(err).__name__}: {err}"
                log.warning(f"Failed to load extension {extension}\n{exc}")
        return clean

    def unload_extensions(self, extensions=None):
        """
            Unloads all extensions in input, or all extensions currently loaded if None
            :param extensions: List of extensions to unload, or None if all
        """
        log.info("Unloading multiple extensions")
        if extensions is None:
            while len(self.extensions) > 0:
                extension = self.extensions.popitem()
                log.debug(f"Unloading extension {extension}")
                self.unload_extension(extension, False)
        else:
            for extension in extensions:
                log.debug(f"Unloading extension {extension}")
                self.unload_extension(extension)

    def find_command(self, command):
        """
            Given a string command, attempts to find it iteratively through command groups
        :param command: Command to find in Talos. Can have spaces if necessary
        :return: Command object if found, None otherwise
        """
        if command in self.all_commands:
            return self.all_commands[command]
        command = command.split(" ")
        if len(command) > 1:
            cur = self
            for sub in command:
                cur = cur.all_commands.get(sub)
                if cur is None:
                    return None
            return cur
        return None
