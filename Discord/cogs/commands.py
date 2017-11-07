"""
    Commands cog for Talos
    Holds all commands usable by any user, and a couple of classes relevant to those commands.

    Author: CraftSpider
"""
import discord
from discord.ext import commands
import asyncio
import random
import logging
import re
from datetime import datetime
from datetime import timedelta
from collections import defaultdict
from utils import PW


# Dict to keep track of whatever the currently active PW is
active_pw = defaultdict(lambda: None)

logging = logging.getLogger("talos.command")


def perms_check():
    """Determine whether the person calling the command is an operator or admin."""
    def predicate(ctx):

        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            return True
        command = str(ctx.command)

        try:
            if not ctx.bot.database.get_guild_option(ctx.guild.id, "commands"):
                return False
        except KeyError:
            pass
        perms = ctx.bot.database.get_perm_rules(ctx.guild.id, command)
        if len(perms) == 0:
            return True
        perms.sort(key=lambda x: x[3])
        for perm in perms:
            if perm[1] == "user" and perm[2] == str(ctx.author):
                return perm[4]
            elif perm[1] == "role":
                for role in ctx.author.roles:
                    if perm[2] == str(role):
                        return perm[4]
            elif perm[1] == "channel" and perm[2] == str(ctx.channel):
                return perm[4]
            elif perm[1] == "guild":
                return perm[4]
        return True

    return commands.check(predicate)


def sort_mem(member):
    """Function key for sorting PW_Member objects."""
    return member.end - member.start


def strfdelta(time_delta, fmt):
    """A way to convert time deltas to string formats easily."""
    d = {"d": time_delta.days}
    d["h"], rem = divmod(time_delta.seconds, 3600)
    d["m"], d["s"] = divmod(rem, 60)
    return fmt.format(**d)


def html_to_markdown(html):
    html = re.sub(r"</p>|<br>", "\n", html)
    html = re.sub(r"<strong>|</strong>", "**", html)
    html = re.sub(r"<em>|</em>", "*", html)
    html = re.sub(r"<a.*?href=\"(.*?)\".*?>(.*?)</a>", "[\g<2>](\g<1>)", html)
    html = re.sub(r"<li>", "- ", html)
    html = re.sub(r"<.*?>\n?", "", html)
    return html


class Commands:
    """These commands can be used by anyone, as long as Talos is awake.\nThey don't care who is using them."""

    __slots__ = ['bot', 'database']

    def __init__(self, bot):
        """Initialize the Commands cog. Takes in an instance of Talos to use while running."""
        self.bot = bot
        self.database = None
        if hasattr(bot, "database"):
            self.database = bot.database

    def get_uptime_days(self):
        """Gets the amount of time Talos has been online in days, hours, minutes, and seconds. Returns a string."""
        time_delta = datetime.now() - self.bot.BOOT_TIME
        delta_string = strfdelta(time_delta,
                                 "{d} day" + ("s" if time_delta.days != 1 else "") + ", {h:02}:{m:02}:{s:02}") \
            .format(x=("s" if time_delta.days == 1 else ""))
        return delta_string

    def get_uptime_percent(self):
        """Gets the percentages of time Talos has been up over the past day, month, and week."""
        now = datetime.now().replace(microsecond=0)
        day_total = 24 * 60
        week_total = day_total * 7
        month_total = day_total * 30
        day_up = len(self.database.get_uptime(int((now - timedelta(days=1)).timestamp()))) / day_total * 100
        week_up = len(self.database.get_uptime(int((now - timedelta(days=7)).timestamp()))) / week_total * 100
        month_up = len(self.database.get_uptime(int((now - timedelta(days=30)).timestamp()))) / month_total * 100
        return day_up, week_up, month_up

    #
    #   Generator Strings
    #
    noun = ["dog", "cat", "robot", "astronaut", "man", "woman", "person", "child", "giant", "elephant", "zebra",
            "animal", "box", "tree", "wizard", "mage", "swordsman", "soldier", "inventor", "doctor", "Talos", "East"
            "dinosaur", "insect", "nerd", "dancer", "singer", "actor", "barista", "acrobat", "gamer", "writer",
            "dragon"]
    adjective = ["happy", "sad", "athletic", "giant", "tiny", "smart", "silly", "unintelligent", "funny",
                 "coffee-loving", "lazy", "spray-tanned", "angry", "disheveled", "annoying", "loud", "quiet", "shy",
                 "extroverted", "jumpy", "ditzy", "strong", "weak", "smiley", "annoyed", "dextrous"]
    goal = ["fly around the world", "go on a date", "win a race", "tell their crush how they feel",
            "find their soulmate", "write a chatbot", "get into university", "graduate high school",
            "plant a hundred trees", "find their biological parents", "fill their bucket list", "find atlantis",
            "learn magic", "learn to paint", "drive a car", "pilot a spaceship", "leave Earth", "go home",
            "redo elementary school", "not spill their beer"]
    obstacle = ["learning to read", "fighting aliens", "saving the world", "doing algebra", "losing their hearing",
                "losing their sense of sight", "learning the language", "hacking the mainframe", "coming of age",
                "the nuclear apocalypse is happening", "incredibly drunk", "drinking coffee", "surfing",
                "spying on the bad guys", "smelling terrible", "having a bad hair day", "exploring the new planet",
                "on the moon", "on Mars"]
    
    place = ["pub", "spaceship", "museum", "office", "jungle", "forest", "coffee shop", "store", "market", "station",
             "tree", "hut", "house", "bed", "bus", "car", "dormitory", "school", "desert", "ballroom", "cattery",
             "shelter", "street"]
    place_adjective = ["quiet", "loud", "crowded", "deserted", "bookish", "colorful", "balloon-filled", "book", "tree",
                       "money", "video game", "cat", "dog", "busy", "apocalypse", "writer", "magic", "light", "dark",
                       "robotic", "futuristic", "old-timey"]
    action = ["learn to read", "jump up and down", "cry a lot", "cry a little", "smile", "spin in a circle",
              "get arrested", "dance to the music", "listen to your favourite song", "eat all the food",
              "win the lottery", "hack the mainframe", "save the world", "find atlantis", "get accepted to Hogwarts",
              "swim around", "defy gravity", "spy on the bad guys", "drive a car", "enter the rocket ship",
              "learn math", "write a lot", "do gymnastics"]

    phrases = ["Hello World!", "Hephaestus and Daedalus are my favorite people", "This is a footer message",
               "I can't wait to see East again", "I'm here to help.", "My devs are all crazy"]

    #
    #   User Commands
    #
    
    @commands.command(aliases=["info"])
    @perms_check()
    async def information(self, ctx):
        """Gives a short blurb about Talos."""
        if self.bot.should_embed(ctx):
            description = "Hello! I'm Talos, official PtP Mod-Bot and general writing helper.\n"\
                          "`{}help` to see a list of my commands."
            embed = discord.Embed(
                title="Talos Information",
                colour=discord.Colour(0x202020),
                description=description.format((await self.bot.get_prefix(ctx))[0]),
                timestamp=datetime.now()
            )
            embed.set_footer(text="{}".format(random.choice(self.phrases)))
            embed.add_field(name="Developers", value="CraftSpider#0269\nDino\nHiddenStorys", inline=True)
            embed.add_field(name="Library", value="Discord.py\nVersion {}".format(discord.__version__), inline=True)
            embed.add_field(name="Contact/Documentation",
                            value="[talos.ptp@gmail.com](mailto:talos.ptp@gmail.com)\n"
                                  "[Github](http://github.com/CraftSpider/TalosBot)\n"
                                  "[Discord](http://discord.gg/VxUdS6H)",
                            inline=True)

            uptime_str = "{}\n{:.0f}% Day, {:.0f}% Week, {:.0f}% Month".format(self.get_uptime_days(),
                                                                               *self.get_uptime_percent())
            embed.add_field(name="Uptime", value=uptime_str, inline=True)
            stats_str = "I'm in {} Guilds,\nWith {} Users.".format(len(self.bot.guilds), len(self.bot.users))
            embed.add_field(name="Statistics", value=stats_str, inline=True)
            await ctx.send(embed=embed)
        else:
            out = "Hello! I'm Talos, official PtP mod-bot. `{}help` for command details.\
                    \nMy Developers are CraftSpider, Dino, and HiddenStorys.\
                    \nI am built using discord.py, version {}.\
                    \nAny suggestions or bugs can be sent to my email, talos.ptp@gmail.com.".format(
                (await self.bot.get_prefix(ctx))[0], discord.__version__)
            await ctx.send(out)

    @commands.command()
    @perms_check()
    async def discord_tos(self, ctx):
        """Disclaimer for discord TOS"""
        await ctx.send("Talos will in the process of running possibly log your username and log commands that you give "
                       "it. Due to Discord TOS, you must be informed and consent to any storage of data you send here. "
                       "This data will never be publicly shared except at your request, and only used to help run Talos"
                       " and support features that require it. If you have any questions about this or problems with it"
                       ", please talk to one of the Talos developers for information and we'll see what we can do to "
                       "help")

    @commands.command()
    @perms_check()
    async def version(self, ctx):
        """Returns Talos version."""
        await ctx.send("Version: {0}".format(self.bot.VERSION))

    @commands.command()
    @perms_check()
    async def roll(self, ctx, dice: str):
        """Rolls dice in NdN format."""
        try:
            rolls, limit = map(int, dice.lower().split('d'))
        except ValueError:
            await ctx.send('Format has to be in NdN!')
            return
        try:
            result = ', '.join(str(random.randint(1, limit)) for _ in range(rolls))
        except ValueError:
            await ctx.send("Minimum second value is 1")
            return
        if result is "":
            await ctx.send("Minimum first value is 1")
            return
        await ctx.send(result)
        
    @commands.command(description='For when you wanna settle the score some other way',
                      usage="[choice 1], [choice 2], ...")
    @perms_check()
    async def choose(self, ctx, *choices: str):
        """Chooses between multiple choices."""
        choices = " ".join(choices)
        if "," not in choices:
            await ctx.send("I need at least two choices to choose between!")
            return
        out = "I'm choosing between: {}.\n".format(choices)
        if random.randint(1, 500) == 1:
            out += "None of the above"
        elif random.randint(1, 500) == 500:
            out += "All of the above"
        else:
            choices = choices.split(",")
            out += random.choice(choices).strip()
        await ctx.send(out)

    @commands.command()
    @perms_check()
    async def time(self, ctx):
        """Prints out the current time in UTC, HH:MM:SS format"""
        await ctx.send("It's time to get a watch. {0}".format(datetime.utcnow().strftime("%H:%M:%S")))
    
    @commands.command(aliases=["ww", "WW"])
    @perms_check()
    async def wordwar(self, ctx, length: str="", start: str="", wpm: int=30):
        """Runs an X minute long word-war"""
        try:
            length = float(length)
        except ValueError:
            await ctx.send("Please specify the length of your word war (in minutes).")
            return
        if length > 60 or length < 1:
            await ctx.send("Please choose a length between 1 and 60 minutes.")
            return
        if wpm < 0:
            await ctx.send("Please choose a non-negative WPM.")
            return

        if start:
            try:
                if start[0] == ":":
                    start = int(start[1:])
                elif start[0].isnumeric():
                    start = int(start)
                else:
                    raise ValueError
            except ValueError:
                await ctx.send("Start time format broken. Starting now.")
                start = ""
            if start != "" and (start > 59 or start < 0):
                await ctx.send("Please specify a start time in the range of 0 to 59.")
                return

        if start is not "":
            now = datetime.utcnow()
            dif = abs(now - now.replace(hour=(now.hour if start > now.minute else (now.hour + 1) % 24), minute=start,
                                        second=0))
            await ctx.send("Starting WW at :{0:02}".format(start))
            await asyncio.sleep(dif.total_seconds())
        await ctx.send("Word War for {:g} {}.".format(length, "minutes" if length != 1 else "minute"))
        await asyncio.sleep(length * 60)

        words_written = wpm * length
        advance = False
        while not advance and wpm != 0:
            words_written = random.randrange(words_written-100, words_written+100)
            if words_written >= 0:
                advance = True
        if wpm != 0:
            await ctx.send("I wrote {} words. How many did you write?".format(words_written))
        else:
            await ctx.send("The word war is over. How did you do?")

    @commands.command()
    @perms_check()
    async def credits(self, ctx):
        """Giving credit where it is due"""
        await ctx.send("Primary Developers: CraftSpider, Dino.\n"
                       "Other contributors: Wundrweapon, HiddenStorys\n"
                       "Artist: Misty Tynan")
    
    @commands.command()
    @perms_check()
    async def joined(self, ctx, member: discord.Member):
        """Says when a member joined."""
        await ctx.send('{0.name} joined in {0.joined_at}'.format(member))
    
    @commands.command()
    @perms_check()
    async def uptime(self, ctx):
        """To figure out how long the bot has been online."""
        boot_string = self.bot.BOOT_TIME.strftime("%b %d, %H:%M:%S")
        out = "I've been online since {0}, a total of {1}\n".format(boot_string, self.get_uptime_days())
        day_up, week_up, month_up = self.get_uptime_percent()
        out += "Past uptime: {:02.2f}% of the past day, ".format(day_up)
        out += "{:02.2f}% of the past week, ".format(week_up)
        out += "{:02.2f}% of the past month".format(month_up)
        await ctx.send(out)

    @commands.command()
    @perms_check()
    async def ping(self, ctx):
        """Checks the Talos delay. (Not round trip. Time between putting message and gateway acknowledgement.)"""
        start = datetime.now()
        await self.bot.get_user_info(101091070904897536)
        end = datetime.now()
        milliseconds = (end - start).microseconds/1000
        await ctx.send("Current Ping: `{}`".format(milliseconds))

    @commands.group(aliases=["nano"])
    @perms_check()
    async def nanowrimo(self, ctx):
        """Fetches info from the NaNo site"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'novel' and 'profile'.")

    @nanowrimo.command(name="novel")
    async def _novel(self, ctx, username: str, novel_name: str=""):
        """Fetches detailed info on a user's novel from the NaNo site"""
        username = username.lower().replace(" ", "-")
        novel_name = novel_name.lower().replace(" ", "-")

        novel_page, novel_stats = await self.bot.session.nano_get_novel(username, novel_name)
        if novel_page is None:
            await ctx.send("Sorry, I couldn't find that user or novel.")
            return
        # Get basic novel info
        avatar = "https:" + re.search(r"<img alt=\".*?\" class=\".*?avatar_thumb.*?\" src=\"(.*?)\" />", novel_page).group(1)
        novel_title = re.search(r"<strong>Novel:</strong>\n(.*)", novel_page).group(1)
        novel_cover = re.search(r"<img .*?id=\"novel_cover_thumb\".*?src=\"(.*?)\" />", novel_page)
        if novel_cover is not None:
            novel_cover = "https:" + novel_cover.group(1)
        novel_genre = re.search(r"<strong>Genre:</strong>\n(.*)", novel_page).group(1)
        novel_synopsis = html_to_markdown(re.search(r"<div id='novel_synopsis'>(.*?)</div>", novel_page, re.S).group(1))
        if novel_synopsis.strip() == "":
            novel_synopsis = None
        elif len(novel_synopsis) > 1024:
            novel_synopsis = novel_synopsis[:1021] + "..."
        novel_excerpt = html_to_markdown(re.search(r"<div id='novel_excerpt'>(.*?)</div>", novel_page, re.S).group(1))
        if novel_excerpt.strip() == "":
            novel_excerpt = None
        elif len(novel_excerpt) > 1024:
            novel_excerpt = novel_excerpt[:1021] + "..."
        # Get novel statistics
        base_regex = r"<div class='title'>{}</div>\n<div class='value'>\n?(.*?)(?:\n|</div>)"
        titles = ["Your Average Per Day", "Words Written Today", "Total Words Written",
                  "Target Average Words Per Day", "Words Remaining"]
        stats = []
        for item in titles:
            stats.append(
                int(re.search(base_regex.format(item), novel_stats).group(1).replace(",", ""))
            )
        stats[3] = stats[3] - stats[1]
        if self.bot.should_embed(ctx):
            # Construct Embed
            description = "*Title:* {} *Genre:* {}\n**Wordcount Details**\n".format(novel_title, novel_genre)
            description += "Daily Avg: {:,}\n".format(stats[0])
            description += "Words Today: {:,}\n".format(stats[1])
            description += "Words Total: {:,}\n".format(stats[2])
            description += "Remaining Today: {:,}\n".format(stats[3])
            description += "Remaining Total: {:,}\n".format(stats[4])
            embed = discord.Embed(title="__Novel Details__", description=description)
            embed.set_author(name=username, icon_url=avatar)
            if novel_cover is not None:
                embed.set_thumbnail(url=novel_cover)
            if novel_synopsis is not None:
                embed.add_field(name="__Synopsis__", value=novel_synopsis)
            if novel_excerpt is not None:
                embed.add_field(name="__Excerpt__", value=novel_excerpt)
            await ctx.send(embed=embed)

    @nanowrimo.command(name="profile")
    async def _profile(self, ctx, username: str):
        """Fetches a given username's profile from the NaNo site"""
        sitename = username.lower().replace(" ", "-")
        sitename = sitename.lower().replace(".", "-")

        page = await self.bot.session.nano_get_user(sitename)
        if page is None:
            await ctx.send("Sorry, I couldn't find that user on the NaNo site.")
            return
        # Get member info
        member_age = re.search(r"<div class='member_for'>(.*?)</div>", page).group(1)
        author_bio = re.search(r"<h3>Author Bio</h3>.*?<div class='panel-body'>(.*?)</div>", page, re.S)
        if author_bio is not None:
            author_bio = author_bio.group(1)
            author_bio = html_to_markdown(author_bio)
            if len(member_age) + len(author_bio) > 2048:
                author_bio = author_bio[:2048 - len(member_age) - 7] + "..."
                print(len(author_bio) + len(member_age))
        else:
            author_bio = ""
        avatar = "https:" + re.search(r"<img alt=\".*?\" class=\".*?avatar_thumb.*?\" src=\"(.*?)\" />", page).group(1)
        # Get basic novel stats
        novel_title = re.search(r"<strong>Novel:</strong>\n(.*)", page)
        if novel_title is not None:
            novel_title = novel_title.group(1)
            novel_genre = re.search(r"<strong>Genre:</strong>\n(.*)", page).group(1)
            novel_words = re.search(r"<strong>(\d*)</strong>\nwords so far", page).group(1)
        else:
            novel_genre = None
            novel_words = None
        # Get fact sheet
        fact_sheet = re.search(r"<dl>(.*?)</dl>", page, flags=re.S).group(1)
        if fact_sheet.strip() != "":
            fact_sheet = re.sub(r"<dd>|</dd>", "", fact_sheet)
            fact_sheet = re.sub(r"<dt>|</dt>", "**", fact_sheet)
            fact_sheet = re.sub(r"\*\*Website:\*\*\n<.*?href=\"http://\".*?>.*?</a>\n?", "", fact_sheet)
            fact_sheet = re.sub(r"<a.*?href=\"(.*?)\".*?>(.*?)</a>", "[\g<2>](\g<1>)", fact_sheet)
        else:
            fact_sheet = None
        if self.bot.should_embed(ctx):
            # Build Embed
            embed = discord.Embed(title="__Author Info__", description="*{}*\n\n".format(member_age) + author_bio)
            embed.set_author(name=username, url="http://nanowrimo.org/participants/" + sitename, icon_url=avatar)
            embed.set_thumbnail(url=avatar)
            if novel_title is not None:
                embed.add_field(
                    name="__Novel Info__",
                    value="**Title:** {}\n**Genre:** {}\n**Words:** {}".format(novel_title, novel_genre, novel_words)
                )
            if fact_sheet is not None:
                embed.add_field(
                    name="__Fact Sheet__",
                    value=fact_sheet
                )
            await ctx.send(embed=embed)
        else:
            out = "__**{}**__\n".format(username)
            while len(author_bio) > 200:
                match = re.search(r"\.[^.]*?(?!\.)$", author_bio)
                if match is not None:
                    author_bio = author_bio[:match.start()] + out[match.end():]
                else:
                    author_bio = author_bio[:197] + "..."
            out += "*{}*\n{}\n".format(member_age, author_bio)
            out += "__**Novel Info**__\n"
            out += "**Title:** {} **Genre:** {} **Words:** {}".format(novel_title, novel_genre, novel_words)
            # TODO Add fact sheet
            await ctx.send(out)
    
    @commands.group()
    @perms_check()
    async def generate(self, ctx):
        """Generates a crawl or prompt"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'prompt' and 'crawl'.")
    
    @generate.command(name='crawl')
    async def _crawl(self, ctx):
        """Generates a crawl"""
        place_adj = random.choice(self.place_adjective)
        place = random.choice(self.place)
        words = str(random.randint(50, 500))
        action = random.choice(self.action)
        await ctx.send("You enter the {} {}. Write {} words as you {}.".format(place_adj, place, words, action))
    
    @generate.command(name='prompt')
    async def _prompt(self, ctx):
        """Generates a prompt"""
        adj = random.choice(self.adjective)
        noun = random.choice(self.noun)
        goal = random.choice(self.goal)
        obstacle = random.choice(self.obstacle)
        await ctx.send("A story about a {} {} who must {} while {}.".format(adj, noun, goal, obstacle))

    @commands.group(aliases=["pw", "PW"])
    @commands.guild_only()
    @perms_check()
    async def productivitywar(self, ctx):
        """Commands for a productivity war."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'create', 'join', 'start', 'leave', and 'end'.")

    @productivitywar.command(name='create')
    async def _create(self, ctx):
        """Begins a new PW, if one isn't already running."""
        if active_pw[ctx.guild.id] is not None:
            await ctx.send("There's already a PW going on. Would you like to **join**?")
        else:
            await ctx.send("Creating a new PW.")
            active_pw[ctx.guild.id] = PW()
            active_pw[ctx.guild.id].join(ctx.author)

    @productivitywar.command(name='join')
    async def _join(self, ctx):
        """Join a currently running PW, if you aren't already in it."""
        if active_pw[ctx.guild.id] is not None:
            if active_pw[ctx.guild.id].join(ctx.author):
                await ctx.send("User {} joined the PW.".format(ctx.author.display_name))
            else:
                await ctx.send("You're already in this PW.")
        else:
            await ctx.send("No PW to join. Maybe you want to **create** one?")

    @productivitywar.command(name='start')
    async def _start(self, ctx, time=""):
        """Start a PW that isn't yet begun."""
        if active_pw[ctx.guild.id] is not None:
            if not active_pw[ctx.guild.id].get_started():
                if time != "" and time[0] == ":":
                    try:
                        time = int(time[1:])
                        if time < 0 or time > 59:
                            ctx.send("Please give a time between 0 and 60.")
                            return
                        now = datetime.now()
                        time_delta = abs(now - now.replace(hour=(now.hour if time > now.minute else (now.hour+1 % 24)),
                                                           minute=time, second=0))
                        await ctx.send("Starting PW at :{:02}".format(time))
                        await asyncio.sleep(time_delta.total_seconds())
                    except ValueError:
                        ctx.send("Time needs to be a number.")
                await ctx.send("Starting PW")
                active_pw[ctx.guild.id].begin()
            else:
                await ctx.send("PW has already started! Would you like to **join**?")
        else:
            await ctx.send("No PW to start. Maybe you want to **create** one?")

    @productivitywar.command(name='leave')
    async def _leave(self, ctx):
        """End your involvement in a PW, if you're the last person, the whole thing ends."""
        if active_pw[ctx.guild.id] is not None:
            leave = active_pw[ctx.guild.id].leave(ctx.author)
            if leave == 0:
                await ctx.send("User {} left the PW.".format(ctx.author.display_name))
            elif leave == 1:
                await ctx.send("You aren't in the PW! Would you like to **join**?")
            elif leave == 2:
                await ctx.send("You've already left this PW! Are you going to **end** it?")
            if active_pw[ctx.guild.id].get_finished():
                await self._end.invoke(ctx)
        else:
            await ctx.send("No PW to leave. Maybe you want to **create** one?")

    @productivitywar.command(name='end')
    async def _end(self, ctx):
        """End the whole PW, if one is currently running."""
        if active_pw[ctx.guild.id] is None:
            await ctx.send("There's currently no PW going on. Would you like to **create** one?")
        elif not active_pw[ctx.guild.id].get_started():
            await ctx.send("Deleting un-started PW.")
            active_pw[ctx.guild.id] = None
        else:
            await ctx.send("Ending PW.")
            active_pw[ctx.guild.id].finish()
            cur_pw = active_pw[ctx.guild.id]
            cur_pw.members.sort(key=sort_mem, reverse=True)
            winner = discord.utils.find(lambda m: cur_pw.members[0].user == m, ctx.guild.members)

            if self.bot.should_embed(ctx):
                embed = discord.Embed(colour=winner.colour,
                                      timestamp=datetime.now())
                embed.set_author(name="{} won the PW!".format(winner.display_name), icon_url=winner.avatar_url)
                embed.add_field(name="Start",
                                value="{}".format(cur_pw.start.replace(microsecond=0).strftime("%b %d - %H:%M:%S")),
                                inline=True)
                embed.add_field(name="End",
                                value="{}".format(cur_pw.end.replace(microsecond=0).strftime("%b %d - %H:%M:%S")),
                                inline=True)
                embed.add_field(
                    name="Total",
                    value="{}".format(cur_pw.end.replace(microsecond=0) - cur_pw.start.replace(microsecond=0))
                )
                member_list = ""
                for member in cur_pw.members:
                    member_list += "{0} - {1}\n".format(member.user.display_name, member.get_len())
                embed.add_field(name="Times", value=member_list)
                await ctx.send(embed=embed)
            else:
                out = "```"
                out += "{} won the PW!\n".format(winner.display_name)
                out += "Start: {}\n".format(cur_pw.start.replace(microsecond=0).strftime("%b %d - %H:%M:%S"))
                out += "End: {}\n".format(cur_pw.end.replace(microsecond=0).strftime("%b %d - %H:%M:%S"))
                out += "Total: {}\n".format(cur_pw.end.replace(microsecond=0) - cur_pw.start.replace(microsecond=0))
                out += "Times:\n"
                for member in cur_pw.members:
                    out += "    {0} - {1}\n".format(member.user.display_name, member.get_len())
                out += "```"
                await ctx.send(out)

            active_pw[ctx.guild.id] = None

    @productivitywar.command(name='dump', hidden=True)
    async def _dump(self, ctx):
        """Dumps info about the current state of a running PW"""
        cur_pw = active_pw[ctx.guild.id]
        if cur_pw is None:
            await ctx.send("No PW currently running")
            return
        out = "```"
        out += "Start: {}\n".format(cur_pw.start)
        out += "End: {}\n".format(cur_pw.end)
        out += "Members:\n"
        for member in cur_pw.members:
            out += "    {0} - {1} - {2}\n".format(member, member.start, member.end)
        out += "```"
        await ctx.send(out)


def setup(bot):
    bot.add_cog(Commands(bot))
