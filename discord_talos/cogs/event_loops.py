"""
    Talos regular event loops. Done as a cog so as to keep clutter out of the main file.

    Author: CraftSpider
"""

import os
import pathlib
import httplib2
import logging
import random
import spidertools.common as utils
import spidertools.command_lang as command_lang
import spidertools.discord as dutils
import datetime as dt

from apiclient import discovery
from oauth2client import client, tools, file

# Google API values
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = pathlib.Path(__file__).parent.parent / 'client_secret.dat'
APPLICATION_NAME = 'TalosBot Prompt Reader'

log = logging.getLogger("talos.events")
runner = command_lang.CommandLang(interpreter=command_lang.ContextLessCL())


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    if not pathlib.Path(CLIENT_SECRET_FILE).is_file():
        raise FileNotFoundError("No client secret file")
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-python-quickstart.json')

    store = file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        log.info('Storing credentials to ' + credential_path)
    return credentials


def create_service():
    """Creates and returns a google API service"""
    try:
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        discovery_url = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
        service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discovery_url,
                                  cache_discovery=False)
        return service
    except FileNotFoundError:
        log.warning("Couldn't load client_secret.dat for google services")
        return None


class EventLoops(dutils.TalosCog):
    """Handles the Talos regulated events, time based loops. How did you even figure out this help page existed?"""

    __slots__ = ("service", "last_guild_count")

    def __init__(self, bot):
        """Initialize the EventLoops cog. Takes in an instance of Talos to use while running."""
        super().__init__(bot)
        self.service = None
        self.last_guild_count = 0
        self.setup_prompts()

    def setup_prompts(self):
        """Sets up for the prompts event"""
        self.service = create_service()
        now = dt.datetime.utcnow()
        time = now.replace(hour=self.bot.PROMPT_TIME, minute=0, second=0, microsecond=0)
        if time < now:
            time += dt.timedelta(days=1)
        self.prompt_task.set_start_time(time)

    def get_spreadsheet(self, sheet_id, sheet_range):
        """Get a google spreadsheet range from service"""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=sheet_range).execute()
        return result.get('values', [])

    def set_spreadsheet(self, sheet_id, values, sheet_range=None):
        """Set a google spreadsheet range through service"""
        body = {
            'values': values
        }
        if sheet_range:
            result = self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id, range=sheet_range,
                valueInputOption="RAW", body=body).execute()
        else:
            result = self.service.spreadsheets().values().append(
                spreadsheetId=sheet_id, range=sheet_range,
                valueInputOption="RAW", body=body).execute()
        return result

    @dutils.eventloop("1m", description="Called once at the start of every minute", persist=True)
    async def minute_task(self):
        """Called every minute, checks for guild-specific events and runs any that need to be"""
        for guild in self.bot.guilds:
            events = self.database.get_guild_events(guild.id)
            for event in events:
                period = int(event.period)
                time = int(dt.datetime.now().timestamp())
                current = int(time / period)
                if current > event.last_active:
                    channel = list(filter(lambda x: x.id == event.channel, guild.channels))[0]
                    log.info("Kicking off event " + event.name)
                    await channel.send(runner.exec(channel, event.text))
                    event.last_active = current
                    self.database.save_item(event)

    @dutils.eventloop("1h", description="Called once at the start of every hour", persist=True)
    async def hourly_task(self):
        """Called every hour, and posts current guild amount to DBL if a key is provided and the amount changed"""
        guild_count = len(self.bot.guilds)
        await self.bot.session.botlist_post_guilds(guild_count)

    @dutils.eventloop("1d", description="Called once at the start of every day", persist=True)
    async def daily_task(self):
        """Called every day, and removes old uptimes from the database"""
        self.database.remove_uptime(int((dt.datetime.now() - dt.timedelta(days=30)).timestamp()))
        await self.bot.session.server_post_commands(self.bot.commands_dict())

    @dutils.eventloop("1m", description="Called to add another uptime mark to the database")
    async def uptime_task(self):
        """Called once a minute, to verify uptime. Adds a new row to the uptime table with the current timestamp"""
        self.database.add_uptime(int(dt.datetime.now().replace(microsecond=0).timestamp()))

    @dutils.eventloop("1d", description="Runs the daily prompt task")
    async def prompt_task(self):
        """Once a day, grabs a prompt from google sheets and posts it to the defined prompts chat, if enabled."""
        if self.service is None:
            raise dutils.StopEventLoop("No google service, prompt task quitting")
        prompt_sheet_id = "1bL0mSDGK4ypn8wioQCBqkZH47HmYp6GnmJbXkIOg2fA"
        values = self.get_spreadsheet(prompt_sheet_id, "Form Responses 1!B:E")
        possibilities = []
        values = list(values)
        for item in values:
            if len(item[3:]) == 0:
                possibilities.append(item)
        prompt = random.choice(possibilities)

        log.debug(prompt)
        out = f"__Daily Prompt {dt.date.today().strftime('%m/%d')}__\n\n"
        prompt[0] = prompt[0].strip("\"")
        out += f"{prompt[0]}\n\n"
        original = "Original prompt" if prompt[1].upper() == "YES" else "Submitted"
        out += f"({original} by {prompt[2]})"
        for guild in self.bot.guilds:
            options = self.database.get_guild_options(guild.id)
            if not options.writing_prompts:
                continue
            for channel in guild.channels:
                if channel.name == options.prompts_channel:
                    try:
                        await channel.send(out)
                    except Exception as e:
                        utils.log_error(log, logging.WARNING, e, "Error while attempting to send daily prompt")

        prompt.append("POSTED")
        self.set_spreadsheet(prompt_sheet_id, [prompt],
                             f"Form Responses 1!B{values.index(prompt) + 1}:E{values.index(prompt) + 1}")


def setup(bot):
    """
        Sets up the EventLoops extension. Adds the EventLoops cog to the bot
    :param bot: Bot this extension is being setup for
    """
    bot.add_cog(EventLoops(bot))
