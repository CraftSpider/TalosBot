"""
    Talos regular event loops. Done as a cog so as to keep clutter out of the main file.

    Author: CraftSpider
"""
import os
import httplib2
import asyncio
import logging
import random
import argparse
import utils
import command_lang
import datetime as dt
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

# Google API values
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.dat'
APPLICATION_NAME = 'TalosBot Prompt Reader'

log = logging.getLogger("talos.events")
cl_parser = command_lang.ContextLessCL()


class EventLoops(utils.TalosCog):
    """Handles the Talos regulated events, time based loops. How did you even figure out this help page existed?"""

    __slots__ = ('service', 'flags', 'last_guild_count', 'bg_tasks', "__local_check")

    def __init__(self, bot):
        """Initialize the EventLoops cog. Takes in an instance of Talos to use while running."""
        super().__init__(bot)
        self.service = None
        self.flags = None
        self.last_guild_count = 0
        self.bg_tasks = []

    def __unload(self):
        """Cleans up the cog on unload, cancelling all tasks."""
        for task in self.bg_tasks:
            task.cancel()

    def start_all_tasks(self):
        """Initializes and starts all event tasks"""
        if len(self.bg_tasks) == 0:
            self.start_uptime()
            self.start_prompt()
            self.start_regulars()

    def start_uptime(self):
        """Starts uptime task"""
        self.bg_tasks.append(self.bot.loop.create_task(self.uptime_task()))

    def start_prompt(self):
        """Starts prompts task"""
        self.flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        self.service = self.create_service()
        self.bg_tasks.append(self.bot.loop.create_task(self.prompt_task()))

    def start_regulars(self):
        """Starts regular tasks"""
        self.bg_tasks.append(self.bot.loop.create_task(self.minute_task()))
        self.bg_tasks.append(self.bot.loop.create_task(self.hourly_task()))
        self.bg_tasks.append(self.bot.loop.create_task(self.daily_task()))

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'sheets.googleapis.com-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store, self.flags)
            print('Storing credentials to ' + credential_path)
        return credentials

    def create_service(self):
        """Creates and returns a google API service"""
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        discovery_url = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
        service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discovery_url,
                                  cache_discovery=False)
        return service

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

    async def minute_task(self):
        """Called once at the start of every minute"""
        log.info("Starting minute task")
        now = dt.datetime.now()
        delta = dt.timedelta(seconds=60 - now.second)
        await asyncio.sleep(delta.total_seconds())
        while True:
            for guild in self.bot.guilds:
                events = self.database.get_guild_events(guild.id)
                for event in events:
                    period = int(event.period)
                    time = int(dt.datetime.now().timestamp())
                    current = int(time / period)
                    if current > event.last_active:
                        channel = list(filter(lambda x: x.id == event.channel, guild.channels))[0]
                        log.info("Kicking off event " + event.name)
                        await channel.send(cl_parser.parse_lang(channel, event.text))
                        event.last_active = current
                        self.database.save_item(event)

            delta = dt.timedelta(seconds=60 - now.second)
            await asyncio.sleep(delta.total_seconds())

    async def hourly_task(self):
        """Called once at the top of every hour."""
        log.info("Starting hourly task")
        now = dt.datetime.now()
        delta = dt.timedelta(minutes=60 - now.minute, seconds=60 - now.second)
        await asyncio.sleep(delta.total_seconds())
        while True:
            log.debug("Hourly task runs")
            guild_count = len(self.bot.guilds)
            if self.bot.discordbots_token != "" and guild_count != self.last_guild_count:
                self.last_guild_count = guild_count
                headers = {'Authorization': self.bot.discordbots_token}
                data = {'server_count': guild_count}
                api_url = 'https://discordbots.org/api/bots/199965612691292160/stats'
                await self.bot.session.post(api_url, data=data, headers=headers)

            delta = dt.timedelta(minutes=60 - now.minute, seconds=60 - now.second)
            await asyncio.sleep(delta.total_seconds())

    async def daily_task(self):
        """Called once every day at midnight, does most time-consuming tasks."""
        log.info("Starting daily task")
        now = dt.datetime.now()
        delta = dt.timedelta(hours=24 - now.hour, minutes=60 - now.minute, seconds=60 - now.second)
        await asyncio.sleep(delta.total_seconds())
        while True:
            log.debug("Daily task runs")
            self.database.remove_uptime(int((dt.datetime.now() - dt.timedelta(days=30)).timestamp()))

            delta = dt.timedelta(hours=24 - now.hour, minutes=60 - now.minute, seconds=60 - now.second)
            await asyncio.sleep(delta.total_seconds())

    async def uptime_task(self):
        """Called once a minute, to verify uptime. Old uptimes cleaned once a day."""
        log.info("Starting uptime task")
        delta = dt.timedelta(seconds=60 - dt.datetime.now().replace(microsecond=0).second)
        await asyncio.sleep(delta.total_seconds())
        while True:
            log.debug("Uptime task runs")
            self.database.add_uptime(int(dt.datetime.now().replace(microsecond=0).timestamp()))

            delta = dt.timedelta(seconds=60 - dt.datetime.now().replace(microsecond=0).second)
            await asyncio.sleep(delta.total_seconds())

    async def prompt_task(self):
        """Once a day, grabs a prompt from google sheets and posts it to the defined prompts chat, if enabled."""
        log.info("Starting prompt task")
        now = dt.datetime.now()
        delta = dt.timedelta(hours=(24 - now.hour + (self.bot.PROMPT_TIME-1)) % 24, minutes=60 - now.minute,
                          seconds=60 - now.second)
        await asyncio.sleep(delta.total_seconds())
        while True:
            log.debug("Prompt task runs")
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
                if not self.database.get_guild_options(guild.id).writing_prompts:
                    continue
                for channel in guild.channels:
                    if channel.name == self.database.get_guild_options(guild.id).prompts_channel:
                        await channel.send(out)

            prompt.append("POSTED")
            self.set_spreadsheet(prompt_sheet_id, [prompt],
                                 f"Form Responses 1!B{values.index(prompt) + 1}:E{values.index(prompt) + 1}")

            now = dt.datetime.now()
            delta = dt.timedelta(hours=(24 - now.hour + (self.bot.PROMPT_TIME - 1)) % 24, minutes=60 - now.minute,
                              seconds=60 - now.second)
            await asyncio.sleep(delta.total_seconds())


def setup(bot):
    bot.add_cog(EventLoops(bot))