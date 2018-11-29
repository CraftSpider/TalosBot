
import collections
import datetime as dt

from . import element, errors


_title_transform = {
    "Your Average Per Day": "daily_average",
    "Words Written Today": "total_today",
    "Target Word Count": "target",
    "Target Average Words Per Day": "target_average",
    "Total Words Written": "total",
    "Words Remaining": "words_remaining",
    "Current Day": "current_day",
    "Days Remaining": "days_remaining",
    "At This Rate You Will Finish On": "finish_date",
    "Words Per Day To Finish On Time": "average_to_finish"
}


SimpleNovel = collections.namedtuple("SimpleNovel", "title genre words")


class NanoUser:
    """
        User on the NaNoWrimo site
    """

    __slots__ = ("client", "username", "_avatar", "_age", "_info", "_novels", "_simple_novel")

    def __init__(self, client, username):
        """
            Initialize NaNo user
        :param client: TalosClient this is associated with
        :param username: Username of the current user
        """
        username = username.lower().replace(" ", "-")

        self.client = client
        self.username = username
        self._avatar = None
        self._age = None
        self._info = None
        self._novels = None

    @property
    async def avatar(self):
        """
            Get the avatar of this user
        :return: URL of user avatar
        """
        if self._avatar is None:
            await self._initialize()
        return self._avatar

    @property
    async def age(self):
        """
            Get how long the current user has been part of the NaNo site
        :return: Rough age of the user
        """
        if self._age is None:
            await self._initialize()
        return self._age

    @property
    async def info(self):
        """
            Get the NanoInfo for this user
        :return: NanoInfo object of this user
        """
        if self._info is None:
            await self._initialize()
        return self._info

    @property
    async def novels(self):
        """
            Get the list of novels this user has written
        :return: list of NanoNovel objects
        """
        if self._novels is None:
            await self._init_novels()
        return self._novels

    @property
    async def current_novel(self):
        """
            Get the most recent novel this user has written, or None if they haven't written any
        :return: NanoNovel object
        """
        novels = await self.novels
        if not novels:
            return None
        return novels[0]

    @property
    async def simple_novel(self):
        """
            Get the simple novel representation displayed on the user info page
        :return: SimpleNovel instance
        """
        if self._simple_novel is None:
            await self._initialize()
        return self._simple_novel

    async def _initialize(self):
        """
            Initialize this user, loading their page and parsing the data on it into memory
            Called when an attribute is accessed that is available on this page, and everything is parsed at once
            to prevent loading the page multiple times
        """
        page = await self.client.nano_get_page(f"participants/{self.username}")
        if page is None:
            raise errors.NotAUser(self.username)
        self._info = NanoInfo(page)

        avatar = page.get_first_by_class("avatar_thumb")
        self._avatar = "https:" + avatar.get_attribute("src")

        age = page.get_first_by_class("member_for")
        self._age = age.innertext

        novel_data = page.get_by_class("panel-default")[1].first_child.first_child
        data_marks = page.get_by_tag("li", novel_data)
        novel_title = None
        novel_genre = None
        novel_words = None
        if data_marks:
            novel_title = data_marks[0].innertext
            novel_genre = data_marks[1].innertext
            novel_words = int(data_marks[2].first_child.innertext)
        novel = SimpleNovel(novel_title, novel_genre, novel_words)
        self._simple_novel = novel

    async def _init_novels(self):
        """
            Initialize this user's novels, loading the user novels page and parse all the novels into memory
        """
        page = await self.client.nano_get_page(f"participants/{self.username}/novels")
        if page is None:
            raise errors.NotAUser(self.username)

        novel_els = page.get_by_class("novel")

        novels = []
        for novel_el in novel_els:
            if novel_el.has_class("missing"):
                continue

            novel_el = novel_el.first_child
            year = int(novel_el.first_child.first_child.innertext.split(" ")[1])

            data_el = page.get_first_by_class("media", novel_el)
            cover = None
            if page.get_first_by_class("no_cover", data_el) is None:
                cover = page.get_first_by_class("cover", data_el).first_child.get_attribute("src")

            winner = False
            if len(data_el.child_nodes) == 3:
                winner = True

            data_el = page.get_first_by_class("info", data_el).first_child
            title_el = page.get_first_by_class("media-heading", data_el).first_child
            title = title_el.innertext
            nid = title_el.get_attribute("href").rsplit("/", 1)[-1]
            genre = page.get_first_by_class("genre", data_el).innertext
            synopsis = page.get_first_by_class("ellipsis", data_el).first_child.innerhtml

            novel = NanoNovel(self.client, self, nid)
            novel.year = year
            novel.title = title
            novel.genre = genre
            novel.cover = cover
            novel.winner = winner
            novel.synopsis = synopsis

            novels.append(novel)

        self._novels = novels


class NanoAccount(NanoUser):
    """
        Represents the currently active account. Inherits all the info of a NanoUser, but includes a bit more and
        provides methods to allow manipulation of the values
    """


class NanoInfo:
    """
        User info on the Nano site. Bio, lifetime stats, and their fact sheet
    """

    __slots__ = ("bio", "lifetime_stats", "fact_sheet")

    def __init__(self, page):
        """
            Initialize this NanoInfo object
        :param page: HTML page to parse
        """

        bio_panel = next(filter(lambda x: x.child_nodes[0].innertext == "Author Bio",
                                page.get_by_class("panel-heading")))
        bio_panel = bio_panel.parent.next_child(bio_panel)
        self.bio = bio_panel.innerhtml

        stats = {}
        name = ""
        stats_table = page.get_by_id("lifetime-stats")
        for child in stats_table.child_nodes:
            if not isinstance(child, element.Element):
                continue
            if child.tag == "dt":
                name = child.innertext
            elif child.tag == "dd":
                if name == "Years Done/Won":
                    list = child.first_child.child_nodes
                    data = []
                    for year in list:
                        year = page.get_first_by_class("done_won", year)
                        data.append(int(year.innertext) + 2000)
                    data = tuple(data)
                elif name == "Current NaNo Streak":
                    start = int(child.first_child.first_child.innertext)
                    end = int(child.last_child.first_child.innertext)
                    data = (start + 2000, end + 2000)
                else:
                    data = child.innertext
                stats[name] = data
        self.lifetime_stats = stats

        facts = {}
        name = ""
        fact_table = page.get_first_by_class("profile-fact-sheet").child_nodes[1].first_child
        for child in fact_table.child_nodes:
            if not isinstance(child, element.Element):
                continue
            if child.tag == "dt":
                name = child.innertext
            elif child.tag == "dd":
                if isinstance(child.first_child, element.Element):
                    data = child.first_child.innertext
                else:
                    data = child.innertext
                if not data:
                    continue
                facts[name] = data
        self.fact_sheet = facts


class NanoNovel:
    """
        Novel on the NaNoWriMo site
    """

    __slots__ = ("client", "id", "author", "year", "title", "genre", "cover", "winner", "synopsis", "stats", "_excerpt")

    def __init__(self, client, author, nid):
        """
            Initialize this NanoNovel
        :param client: TalosClient this is associated with
        :param author: NanoUser, the author of this novel
        :param nid: Novel ID, the string for the novel URL
        """
        self.client = client
        self.author = author
        self.id = nid
        self.stats = NanoNovelStats(client, self)

        self.year = None
        self.title = None
        self.genre = None
        self.cover = None
        self.winner = None
        self.synopsis = None
        self._excerpt = None

    @property
    async def excerpt(self):
        """
            Get the novel's excerpt, author chosen short text from the novel
        :return: Novel excerpt
        """
        if not self._excerpt:
            await self._initialize()
        return self._excerpt

    async def _initialize(self):
        """
            Initialize this novel object, loading the novel page and parsing it
        """
        page = await self.client.nano_get_page(f"participants/{self.author.username}/novels/{self.id}")
        if page is None:
            raise errors.NotANovel(self.title)

        self._excerpt = page.get_by_id("novel_excerpt").innerhtml


class NanoAuthoredNovel(NanoNovel):
    """
        Represents a novel authored by the currently active account. Inherits all the info of a NanoNovel, but includes
        a bit more and provides methods to allow manipulation of the values
    """


class NanoNovelStats:
    """
        Detailed stats associated with a NanoNovel
    """

    __slots__ = ("client", "novel", "_daily_average", "_target", "_target_average", "_total_today", "_total",
                 "_words_remaining", "_current_day", "_days_remaining", "_finish_date", "_average_to_finish")

    def __init__(self, client, novel):
        """
            Initialize this Novel stats object
        :param client: TalosClient associated with this object
        :param novel: Novel these stats are for
        """
        self.client = client
        self.novel = novel

        for item in self.__slots__[2:]:
            setattr(self, item, None)

    def __aiter__(self):
        """
            Get an asynchronous iterator from this object. Allows `async for` iteration over this object.
        :return: Asynchronous iterator that yields each stat in form (name, value)
        """
        return self._aiter()

    @property
    def author(self):
        """
            Shorthand to get the author of the associated novel
        :return: Novel author
        """
        return self.novel.author

    @property
    async def daily_average(self):
        """
            The average number of words written per day
        :return: int, words per day
        """
        if self._daily_average is None:
            await self._initialize()
        return self._daily_average

    @property
    async def target(self):
        """
            The target number of words to write this NaNo
        :return: int, target wordcount
        """
        if self._target is None:
            await self._initialize()
        return self._target

    @property
    async def target_average(self):
        """
            The target average number of words per day
        :return: int, target daily average
        """
        if self._target_average is None:
            await self._initialize()
        return self._target_average

    @property
    async def total_today(self):
        """
            The total number of words written today
        :return: int, words written today
        """
        if self._total_today is None:
            await self._initialize()
        return self._total_today

    @property
    async def total(self):
        """
            The total number of words written in this novel
        :return: int, words written total
        """
        if self._total is None:
            await self._initialize()
        return self._total

    @property
    async def words_remaining(self):
        """
            Number of words left to hit the target
        :return: int, words to hit target
        """
        if self._words_remaining is None:
            await self._initialize()
        return self._words_remaining

    @property
    async def current_day(self):
        """
            The current day of the month, if it's currently this novel's NaNo, or None
        :return: int, NaNo day
        """
        if self._current_day is None:
            await self._initialize()
        return self._current_day

    @property
    async def days_remaining(self):
        """
            Days left in this NaNo, if it's currently this book's NaNo, or None
        :return: int, days remaining
        """
        if self._days_remaining is None:
            await self._initialize()
        return self._days_remaining

    @property
    async def finish_date(self):
        """
            The projected day this book will be finished if writing continues at the same pace
        :return: date, projected finish date
        """
        if self._finish_date is None:
            await self._initialize()
        return self._finish_date

    @property
    async def average_to_finish(self):
        """
            The number of words that would need to be written per day to finish on time
        :return: int, average per day to finish
        """
        if self._average_to_finish is None:
            await self._initialize()
        return self._average_to_finish

    async def _aiter(self):
        """
            An asynchronous iterator over all the variable in this Stats object,
            taking the form of (name, stat)
        :return: Asynchronous generator over this object
        """
        if self._daily_average is None:
            await self._initialize()

        for slot in self.__slots__[2:]:
            yield slot, getattr(self, slot)

    async def _initialize(self):
        """
            Initialize this object, loading the detailed stats page and parsing it into memory
        """
        page = await self.client.nano_get_page(f"participants/{self.author.username}/novels/{self.novel.id}/stats")

        stats = page.get_by_id("novel_stats")

        for stat in stats.child_nodes:
            title = stat.first_child.innertext
            value = stat.last_child.innertext

            member = "_" + _title_transform[title]

            if member == "_finish_date":
                value = dt.datetime.strptime(value, "%B %d, %Y").date()
            else:
                value = int(value.replace(",", ""))

            setattr(self, member, value)
