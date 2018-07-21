"""
    Commands cog for Talos
    Holds all commands usable by any user, and a couple of classes relevant to those commands.

    Author: CraftSpider
"""
import discord
import discord.ext.commands as commands
import asyncio
import random
import logging
import re
import utils
import html
import datetime as dt
from collections import defaultdict


# Dict to keep track of whatever the currently active PW is
active_pw = defaultdict(lambda: None)

log = logging.getLogger("talos.command")


def sort_mem(member):
    """Function key for sorting PW_Member objects."""
    return member.end - member.start


def strfdelta(time_delta, fmt):
    """A way to convert time deltas to string formats easily."""
    d = {"d": time_delta.days}
    d["h"], rem = divmod(time_delta.seconds, 3600)
    d["m"], d["s"] = divmod(rem, 60)
    return fmt.format(**d)


def html_to_markdown(html_text):
    html_text = re.sub(r"</p>|<br>", "\n", html_text)
    html_text = re.sub(r"<strong>|</strong>", "**", html_text)
    html_text = re.sub(r"<em>|</em>", "*", html_text)
    html_text = re.sub(r"<a.*?href=\"(.*?)\".*?>(.*?)</a>", "[\g<2>](\g<1>)", html_text)
    html_text = re.sub(r"<li>", "- ", html_text)
    html_text = re.sub(r"<.*?>\n?", "", html_text)
    html_text = html.unescape(html_text)
    return html_text


class Commands(utils.TalosCog):
    """General Talos commands. Get bot info, check the time, or run a wordwar from here. These commands generally """\
        """aren't very user-specific, most commands are in this category."""

    __slots__ = ("__local_check",)

    # keep track of active WWs
    active_wws = {}

    #
    #   Generator Strings
    #
    noun = ["dog", "cat", "robot", "astronaut", "man", "woman", "person", "child", "giant", "elephant", "zebra",
            "animal", "box", "tree", "wizard", "mage", "swordsman", "soldier", "inventor", "doctor", "Talos", "East",
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
    phrases = [
        "Hello World!", "Hephaestus and Daedalus are my favorite people", "This is a footer message",
        "I can't wait to see East again", "I'm here to help", "My devs are all crazy", "The Absolute Love Of Styx",
        "I'm just a glorified Turing Machine", "If I was a ship AI I might be called Stalo",
        "Terrific Artificial Logarithmic Operation Solver", "Top Amorous Locking Oversight Submersible",
        "Terminator After Love Or Salt", "Technically A Literary Operations Sentinel"]

    def get_uptime_days(self):
        """Gets the amount of time Talos has been online in days, hours, minutes, and seconds. Returns a string."""
        time_delta = dt.datetime.utcnow() - self.bot.BOOT_TIME
        delta_string = strfdelta(time_delta,
                                 "{d} day" + ("s" if time_delta.days != 1 else "") + ", {h:02}:{m:02}:{s:02}") \
            .format(x=("s" if time_delta.days == 1 else ""))
        return delta_string

    def get_uptime_percent(self):
        """Gets the percentages of time Talos has been up over the past day, month, and week."""
        now = dt.datetime.utcnow().replace(microsecond=0)
        day_total = 24 * 60
        week_total = day_total * 7
        month_total = day_total * 30
        day_up = len(self.database.get_uptime(int((now - dt.timedelta(days=1)).timestamp()))) / day_total * 100
        week_up = len(self.database.get_uptime(int((now - dt.timedelta(days=7)).timestamp()))) / week_total * 100
        month_up = len(self.database.get_uptime(int((now - dt.timedelta(days=30)).timestamp()))) / month_total * 100
        return day_up, week_up, month_up

    #
    #   User Commands
    #

    @commands.command(description='For when you wanna settle the score some other way',
                      usage="[choice 1], [choice 2], ...")
    async def choose(self, ctx, *, choices):
        """Chooses between multiple choices, as a comma-separated list."""
        if "," not in choices:
            await ctx.send("I need at least two choices to choose between!")
            return
        out = f"I'm choosing between: {choices}.\n"
        if random.randint(1, 500) == 1:
            out += "None of the above"
        elif random.randint(1, 500) == 500:
            out += "All of the above"
        else:
            choices = choices.split(",")
            out += random.choice(choices).strip()
        await ctx.send(out)

    @commands.command(description="Credit where it is due")
    async def credits(self, ctx):
        """Displays credits for Talos, who made what."""
        await ctx.send("Primary Developers: CraftSpider, Dino.\n"
                       "Other contributors: Wundrweapon, HiddenStorys\n"
                       "Artist: Misty Tynan")

    @commands.group(description="Host to all your random generator needs.")
    async def generate(self, ctx):
        """Can generate a crawl, prompt, or name."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'prompt', 'crawl', and 'name'.")

    @generate.command(name='crawl', description="Generates a writing crawl prompt")
    async def _crawl(self, ctx):
        """Generates a writing crawl prompt. Possibly a word count challenge or a WW challenge."""
        form = random.randint(0, 1)
        place_adj = random.choice(self.place_adjective)
        place = random.choice(self.place)
        action = random.choice(self.action)
        out = ""
        if form == 0:
            words = str(random.randint(50, 500))
            out = f"You enter the {place_adj} {place}. Write {words} words as you {action}."
        elif form == 1:
            minutes = str(random.randrange(5, 31, 5))
            out = f"You {action} in the {place_adj} {place}, and you write for {minutes} minutes as you do so."
        await ctx.send(out)

    @generate.command(name="name", description="Generates a random name")
    async def _name(self, ctx, number=1):
        """Generates a name or names. Number must be between 1 and 6. Names are sourced from Behind The Name"""
        if number < 1 or number > 6:
            await ctx.send("Number must be between 1 and 6 inclusive.")
            return
        names = await self.bot.session.btn_get_names(number=number)
        out = ""
        for name in names:
            out += f"{name}\n"
        await ctx.send(out)

    @generate.command(name='prompt', description="Generates a normal writing prompt")
    async def _prompt(self, ctx):
        """Generates a writing prompt sentence. Currently only one sentence form, more coming."""
        adj = random.choice(self.adjective)
        noun = random.choice(self.noun)
        goal = random.choice(self.goal)
        obstacle = random.choice(self.obstacle)
        await ctx.send(f"A story about a {adj} {noun} who must {goal} while {obstacle}.")

    @commands.command(aliases=["info"], description="Displays a short blurb about Talos")
    async def information(self, ctx):
        """Displays such information as who made me, how I'm built, where you can contact me, and more."""
        if self.bot.should_embed(ctx):
            description = "Hello! I'm Talos, official PtP Mod-Bot and general writing helper.\n"\
                          "`{}help` to see a list of my commands.\nPlease donate to support my development on "\
                          "[Patreon](https://www.patreon.com/TalosBot)"
            with utils.PaginatedEmbed() as embed:
                embed.title = "Talos Information"
                embed.colour = discord.Colour(0x202020)
                embed.description = description.format((await self.bot.get_prefix(ctx.message))[0])
                embed.timestamp = dt.datetime.now(tz=self.bot.get_timezone(ctx))
                embed.set_footer(text=f"{random.choice(self.phrases)}")
                embed.add_field(name="Developers", value="CraftSpider#0269\nDino\nHiddenStorys", inline=True)
                embed.add_field(name="Library", value=f"Discord.py\nVersion {discord.__version__}", inline=True)
                embed.add_field(name="Contact/Documentation",
                                value="[Main Website](http://talosbot.org)\n"
                                      "[talos.ptp@gmail.com](mailto:talos.ptp@gmail.com)\n"
                                      "[Github](http://github.com/CraftSpider/TalosBot)\n"
                                      "[Discord](http://discord.gg/VxUdS6H)",
                                inline=True)

                uptime_str = "{}\n{:.0f}% Day, {:.0f}% Week, {:.0f}% Month".format(self.get_uptime_days(),
                                                                                   *self.get_uptime_percent())
                embed.add_field(name="Uptime", value=uptime_str, inline=True)
                stats_str = f"I'm in {len(self.bot.guilds)} Guilds,\nWith {len(self.bot.users)} Users."
                embed.add_field(name="Statistics", value=stats_str, inline=True)
            for page in embed:
                await ctx.send(embed=page)
            # await ctx.send(embed=embed.get_pages())
        else:
            prefix = (await self.bot.get_prefix(ctx.message))[0]
            out = f"Hello! I'm Talos, official PtP mod-bot. `{prefix}help` for command details.\
                    \nMy Developers are CraftSpider, Dino, and HiddenStorys.\
                    \nI am built using discord.py, version {discord.__version__}.\
                    \nAny suggestions or bugs can be sent to my email, talos.ptp@gmail.com.\
                    \nMy primary website is located at http://talosbot.org"
            await ctx.send(out)

    @commands.group(aliases=["nano"], description="Fetch data from the NaNo site")
    async def nanowrimo(self, ctx):
        """Can fetch novels or profiles, with possibly more features coming in time."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'novel' and 'profile'.")

    @nanowrimo.command(name="novel", description="Fetch a user's nano novel.")
    async def _novel(self, ctx, username, novel_name=""):  # TODO: Convert to an HTML Parser
        """Fetches detailed info on a user's novel from the NaNo site. If no novel name is given, it grabs the most """ \
            """recent."""
        username = username.lower().replace(" ", "-")
        novel_name = novel_name.lower().replace(" ", "-")

        novel_page, novel_stats = await self.bot.session.nano_get_novel(username, novel_name)
        if novel_page is None or novel_stats is None:
            await ctx.send("Sorry, I couldn't find that user or novel.")
            return
        # Get basic novel info
        avatar = "https:" + novel_page.get_by_class("avatar_thumb")[0].get_attribute("src")
        novel_title = novel_page.get_by_class("media-heading")[0].innertext
        novel_cover = novel_page.get_by_id("novel_cover_thumb")
        if novel_cover:
            novel_cover = "https:" + novel_cover.get_attribute("src")
        novel_genre = novel_page.get_by_class("genre")[0].innertext
        novel_synopsis = html_to_markdown(novel_page.get_by_id("novel_synopsis").first_child.innertext)
        if novel_synopsis.strip() == "":
            novel_synopsis = None
        elif len(novel_synopsis) > 1024:
            novel_synopsis = novel_synopsis[:1021] + "..."
        novel_excerpt = html_to_markdown(novel_page.get_by_id("novel_excerpt").first_child.innertext)
        if novel_excerpt.strip() == "":
            novel_excerpt = None
        elif len(novel_excerpt) > 1024:
            novel_excerpt = novel_excerpt[:1021] + "..."
        # Get novel statistics
        stats_el = novel_stats.get_by_id("novel_stats")
        stat_list = novel_stats.get_by_class("stat", stats_el)

        title_transform = {
            "Your Average Per Day": "Daily Avg",
            "Words Written Today": "Words Today",
            "Total Words Written": "Words Total",
            "Target Average Words Per Day": "Target Avg",
            "Words Remaining": "Remaining Total"
        }
        stats = {}
        for element in stat_list:
            title = element.child_nodes[0].innertext
            number = element.child_nodes[1].innertext
            stats[title_transform.get(title, title)] = int(number.replace(",", ""))
        if self.bot.should_embed(ctx):
            # Construct Embed
            description = f"*Title:* {novel_title} *Genre:* {novel_genre}\n**Wordcount Details**\n"
            for stat in stats:
                description += f"{stat}: {stats[stat]:,}\n"
            if stats.get("Words Today") and stats.get("Target Avg"):
                description += f"Remaining Total: {stats['Target Avg'] - stats['Words Today']:,}\n"
            with utils.PaginatedEmbed() as embed:
                embed.title = "__Novel Details__"
                embed.description = description
                embed.set_author(name=username, icon_url=avatar)
                if novel_cover is not None:
                    embed.set_thumbnail(url=novel_cover)
                if novel_synopsis is not None:
                    embed.add_field(name="__Synopsis__", value=novel_synopsis)
                if novel_excerpt is not None:
                    embed.add_field(name="__Excerpt__", value=novel_excerpt)
            for page in embed:
                await ctx.send(embed=page)

    @nanowrimo.command(name="profile", description="Fetches a user's profile info.")
    async def _profile(self, ctx, username):
        """Fetches detailed info on a user's profile from the NaNo website."""
        site_name = username.lower().replace(" ", "-")
        site_name = site_name.lower().replace(".", "-")

        doc = await self.bot.session.nano_get_user(site_name)
        if doc is None:
            await ctx.send("Sorry, I couldn't find that user on the NaNo site.")
            return
        # Get member info
        member_age = doc.get_by_class("member_for")[0].innertext
        bio_panel = next(filter(lambda x: x.child_nodes[0].innertext == "Author Bio",
                                doc.get_by_class("panel-heading")))
        author_bio = bio_panel.parent.next_child(bio_panel).first_child.innertext
        if len(member_age) + len(author_bio) > 2048:
            author_bio = author_bio[:2048 - len(member_age) - 7] + "..."
        author_bio = author_bio.strip()
        avatar = "https:" + doc.get_by_class("avatar_thumb")[0].get_attribute("src")
        # Get basic novel stats
        novel_data = doc.get_by_class("panel-default")[1].first_child.first_child
        data_marks = doc.get_by_tag("li", novel_data)
        novel_title = None
        if data_marks:
            novel_title = data_marks[0].innertext
            novel_genre = data_marks[1].innertext
            novel_words = data_marks[2].first_child.innertext
        else:
            novel_genre = None
            novel_words = None
        # Get fact sheet
        fact_sheet = ""
        fact_table = doc.get_by_class("profile-fact-sheet")[0].child_nodes[1].child_nodes[0]
        for child in fact_table.child_nodes:
            if child.tag == "dt":
                fact_sheet += f"**{child.innertext}**\n"
            elif child.tag == "dd":
                fact_sheet += f"{child.innertext}\n"
        if self.bot.should_embed(ctx):
            # Build Embed
            with utils.PaginatedEmbed() as embed:
                embed.title = "__Author Info__"
                embed.description = f"*{member_age}*\n\n" + author_bio
                embed.set_author(name=username, url="http://nanowrimo.org/participants/" + site_name, icon_url=avatar)
                embed.set_thumbnail(url=avatar)
                if novel_title is not None:
                    embed.add_field(
                        name="__Novel Info__",
                        value=f"**Title:** {novel_title}\n**Genre:** {novel_genre}\n**Words:** {novel_words}"
                    )
                if fact_sheet:
                    embed.add_field(
                        name="__Fact Sheet__",
                        value=fact_sheet
                    )
            for page in embed:
                await ctx.send(embed=page)
        else:
            out = f"__**{username}**__\n"
            while len(author_bio) > 200:
                match = re.search(r"\.[^.]*?(?!\.)$", author_bio)
                if match is not None:
                    author_bio = author_bio[:match.start()] + out[match.end():]
                else:
                    author_bio = author_bio[:197] + "..."
            out += f"*{member_age}*\n{author_bio}\n"
            out += "__**Novel Info**__\n"
            out += f"**Title:** {novel_title} **Genre:** {novel_genre} **Words:** {novel_words}\n"
            if fact_sheet is not None:
                fact_sheet = fact_sheet.replace('\n', ' ')
                out += f"__**Fact Sheet**__\n{fact_sheet}"
            await ctx.send(out)

    @commands.command(description="Pong!")
    async def ping(self, ctx):
        """Checks the Talos delay. (Not round trip. Time between putting message and gateway acknowledgement.)"""
        start = dt.datetime.utcnow()
        await self.bot.application_info()
        end = dt.datetime.utcnow()
        milliseconds = (end - start).microseconds / 1000
        await ctx.send(f"Current Ping: `{milliseconds}ms`")

    @commands.group(aliases=["pw", "PW"], description="Want Talos to help you run a productivity war?")
    @commands.guild_only()
    async def productivitywar(self, ctx):
        """Talos productivity war commands. First you create a PW, then people can join it (the creator is """ \
            """automatically added), then once everyone has joined who wants to you can start it.
            Once started, people can leave as they finish, and once everyone is gone the PW will end automatically. """ \
            """Alternatively, you can forcibly end the PW if some people are gone and can't or won't leave."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'create', 'join', 'start', 'leave', and 'end'.")

    @productivitywar.command(name='create', description="Create a new PW if one doesn't exist yet")
    async def _create(self, ctx):
        """Creates a new PW, assuming one doesn't yet exist. There is a limit of one PW per guild at a time."""
        if active_pw[ctx.guild.id] is not None:
            await ctx.send("There's already a PW going on. Would you like to **join**?")
        else:
            await ctx.send("Creating a new PW.")
            active_pw[ctx.guild.id] = utils.PW()
            active_pw[ctx.guild.id].join(ctx.author, self.bot.get_timezone(ctx))

    @productivitywar.command(name='dump', hidden=True, description="Dump the info down the hole")
    async def _dump(self, ctx):
        """Dumps info about the current state of a running PW. Designed for dev purposes."""
        cur_pw = active_pw[ctx.guild.id]
        if cur_pw is None:
            await ctx.send("No PW currently running")
            return
        out = "```"
        out += f"Start: {cur_pw.start}\n"
        out += f"End: {cur_pw.end}\n"
        out += "Members:\n"
        for member in cur_pw.members:
            out += f"    {member} - {member.start} - {member.end}\n"
        out += "```"
        await ctx.send(out)

    @productivitywar.command(name='end', description="End a running PW")
    async def _end(self, ctx):
        """End the whole PW, if one is currently running. Just delete it, if one exists but isn't running."""
        if active_pw[ctx.guild.id] is None:
            await ctx.send("There's currently no PW going on. Would you like to **create** one?")
        elif not active_pw[ctx.guild.id].get_started():
            await ctx.send("Deleting un-started PW.")
            del active_pw[ctx.guild.id]
        else:
            await ctx.send("Ending PW.")
            active_pw[ctx.guild.id].finish(self.bot.get_timezone(ctx))
            cur_pw = active_pw[ctx.guild.id]
            cur_pw.members.sort(key=sort_mem, reverse=True)
            winner = discord.utils.find(lambda m: cur_pw.members[0].user == m, ctx.guild.members)

            if self.bot.should_embed(ctx):
                time = dt.datetime.now(tz=self.bot.get_timezone(ctx))
                with utils.PaginatedEmbed() as embed:
                    embed.colour = winner.colour
                    embed.timestamp = time
                    embed.set_footer(text="")
                    embed.set_author(name=f"{winner.display_name} won the PW!", url=winner.avatar_url)
                    embed.add_field(name="Start",
                                    value=f"{cur_pw.start.replace(microsecond=0).strftime('%b %d - %H:%M:%S')}",
                                    inline=True)
                    embed.add_field(name="End",
                                    value=f"{cur_pw.end.replace(microsecond=0).strftime('%b %d - %H:%M:%S')}",
                                    inline=True)
                    embed.add_field(
                        name="Total",
                        value=f"{cur_pw.end.replace(microsecond=0) - cur_pw.start.replace(microsecond=0)}"
                    )
                    member_list = ""
                    for member in cur_pw.members:
                        member_list += f"{member.user.display_name} - {member.get_len()}\n"
                    embed.add_field(name="Times", value=member_list)
                for page in embed:
                    await ctx.send(embed=page)
            else:
                out = "```"
                out += f"{winner.display_name} won the PW!\n"
                out += f"Start: {cur_pw.start.replace(microsecond=0).strftime('%b %d - %H:%M:%S')}\n"
                out += f"End: {cur_pw.end.replace(microsecond=0).strftime('%b %d - %H:%M:%S')}\n"
                out += f"Total: {cur_pw.end.replace(microsecond=0) - cur_pw.start.replace(microsecond=0)}\n"
                out += "Times:\n"
                for member in cur_pw.members:
                    out += f"    {member.user.display_name} - {member.get_len()}\n"
                out += "```"
                await ctx.send(out)
            del active_pw[ctx.guild.id]

    @productivitywar.command(name='join', description="Join an existing PW")
    async def _join(self, ctx):
        """Signs you up for an existing PW, if you are not already in this one."""
        if active_pw[ctx.guild.id] is not None:
            if active_pw[ctx.guild.id].join(ctx.author, self.bot.get_timezone(ctx)):
                await ctx.send(f"User {ctx.author.display_name} joined the PW.")
            else:
                await ctx.send("You're already in this PW.")
        else:
            await ctx.send("No PW to join. Maybe you want to **create** one?")

    @productivitywar.command(name='leave', description="Leave a PW you've joined")
    async def _leave(self, ctx):
        """End your involvement in a PW. If you're the last person out, the whole thing ends."""
        if active_pw[ctx.guild.id] is not None:
            leave = active_pw[ctx.guild.id].leave(ctx.author, self.bot.get_timezone(ctx))
            if leave == 0:
                await ctx.send(f"User {ctx.author.display_name} left the PW.")
            elif leave == 1:
                await ctx.send("You aren't in the PW! Would you like to **join**?")
            elif leave == 2:
                await ctx.send("You've already left this PW! Are you going to **end** it?")
            if active_pw[ctx.guild.id].get_finished():
                # await self._end.invoke(ctx)
                await self.productivitywar.all_commands["end"].invoke(ctx)
        else:
            await ctx.send("No PW to leave. Maybe you want to **create** one?")

    @productivitywar.command(name='start', description="Start an un-started PW")
    async def _start(self, ctx, time=""):
        """Start a PW that isn't yet begun. Ready, set... GO!"""
        if active_pw[ctx.guild.id] is not None:
            if not active_pw[ctx.guild.id].get_started():
                if time != "" and time[0] == ":":
                    try:
                        time = int(time[1:])
                        if time < 0 or time > 59:
                            ctx.send("Please give a time between 0 and 60.")
                            return
                        now = dt.datetime.now(tz=self.bot.get_timezone(ctx))
                        time_delta = abs(
                            now - now.replace(hour=(now.hour if time > now.minute else (now.hour + 1 % 24)),
                                              minute=time, second=0))
                        await ctx.send(f"Starting PW at :{time:02}")
                        await asyncio.sleep(time_delta.total_seconds())
                    except ValueError:
                        ctx.send("Time needs to be a number.")
                await ctx.send("Starting PW")
                active_pw[ctx.guild.id].begin(self.bot.get_timezone(ctx))
            else:
                await ctx.send("PW has already started! Would you like to **join**?")
        else:
            await ctx.send("No PW to start. Maybe you want to **create** one?")

    @commands.command(description="Allows the rolling of dice")
    async def roll(self, ctx, dice):
        """Dice are rolled in NdN format, Number of dice first, then how many sides they have."""
        try:
            rolls, limit = map(int, dice.lower().split("d"))
        except ValueError:
            await ctx.send("Format has to be in NdN!")
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

    @commands.command(description="It's time to get a watch")
    async def time(self, ctx, timezone=None):
        """Prints out the current guild time, HH:MM:SS format. If provided, timezone should be a timezone """ \
            """shorthand such as EST or of the format [+/-]hhmm, for example +0500."""
        if not timezone:
            tz = self.bot.get_timezone(ctx)
        else:
            if utils.tz_map.get(timezone):
                tz = dt.timezone(dt.timedelta(hours=utils.tz_map[timezone]), timezone)
            else:
                try:
                    timezone = float(timezone)
                except ValueError:
                    await ctx.send("Invalid timezone format")
                    return
                if -24 < timezone < 24:
                    name = f"{int(timezone * 100):+05}"
                    tz = dt.timezone(dt.timedelta(hours=timezone), name)
                elif -2360 < timezone <= 2360:
                    timezone = timezone / 100
                    hours, minutes = str(timezone).split(".")
                    if len(minutes) == 1:
                        minutes = str(int(minutes) * 10)
                    hours = int(hours)
                    minutes = int(minutes)
                    name = f"{int(timezone * 100):+05}"
                    tz = dt.timezone(dt.timedelta(hours=hours, minutes=minutes), name)
                else:
                    await ctx.send("Offset must be between -24 hours and 24 hours, exclusive.")
                    return
        await ctx.send(
            f"It's time to get a watch. {dt.datetime.now(tz=tz).strftime('%H:%M:%S')} {tz.tzname(None)}"
        )

    @commands.command(description="Disclaimer for discord TOS")
    async def tos(self, ctx):
        """Also known as the 'don't report me' command"""
        await ctx.send("Talos will in the process of running possibly log your username and log commands that you give "
                       "it. Due to Discord TOS, you must be informed and consent to any storage of data you send here. "
                       "This data will never be publicly shared except at your request, and only used to help run Talos"
                       " and support features that require it. If you have any questions about this or problems with it"
                       ", please talk to one of the Talos developers for information and we'll see what we can do to "
                       "help")

    @commands.command(description="Displays how long the bot has been online")
    async def uptime(self, ctx):
        """Displays details of uptime. Current uptime length and percentages with """ \
            """precision"""
        boot_string = self.bot.BOOT_TIME.strftime("%b %d, %H:%M:%S")
        out = f"I've been online since {boot_string}, a total of {self.get_uptime_days()}\n"
        day_up, week_up, month_up = self.get_uptime_percent()
        out += f"Past uptime: {day_up:02.2f}% of the past day, "
        out += f"{week_up:02.2f}% of the past week, "
        out += f"{month_up:02.2f}% of the past month"
        await ctx.send(out)

    @commands.command(description="Display Talos version")
    async def version(self, ctx):
        """Version is formatted in [major-minor-patch] style."""
        await ctx.send(f"Version: {self.bot.VERSION}")
    
    @commands.command(aliases=["ww", "WW"], description="Have Talos help run a Word War")
    async def wordwar(self, ctx, length, start="", name="", wpm: int=30):
        """Runs a word war for a given length. A word war being a multi-person race to see who can get the greatest """\
            """number of words in the given time period. `^wordwar cancel [id]` to cancel a running ww."""
        if length.lower() == "cancel":
            try:
                start = int(start) - 1
            except ValueError:
                await ctx.send("ID must be a number.")
                return
            try:
                self.active_wws[start].cancel()
            except KeyError:
                await ctx.send("That WW either doesn't exist or is already over.")
                return
            del self.active_wws[start]
            await ctx.send("WW cancelled!")
            return
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

        dif = dt.timedelta(0)
        if start is not "":
            now = dt.datetime.now(tz=self.bot.get_timezone(ctx))
            dif = abs(now - now.replace(hour=(now.hour if start > now.minute else (now.hour + 1) % 24), minute=start,
                                        second=0))

        async def active_wordwar():
            ww_name = (wwid + 1 if isinstance(wwid, int) else wwid.rstrip("_"))
            if start is not "":
                await ctx.send(f"Starting WW {ww_name} at :{start:02}")
                await asyncio.sleep(dif.total_seconds())
            minute = 'minutes' if length != 1 else 'minute'
            await ctx.send(f"Word War {ww_name} for {length:g} {minute}.")
            await asyncio.sleep(length * 60)

            if wpm != 0:
                words_written = int(wpm * length + random.randint(-2 * length, 2 * length))
                await ctx.send(f"I wrote {words_written} words. How many did you write?")
            else:
                await ctx.send("The word war is over. How did you do?")
            del self.active_wws[wwid]

        task = self.bot.loop.create_task(active_wordwar())
        wwid = name or 0
        while self.active_wws.get(wwid):
            if isinstance(wwid, str):
                wwid += "_"
            else:
                wwid += 1
        self.active_wws[wwid] = task


def setup(bot):
    bot.add_cog(Commands(bot))