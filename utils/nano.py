
import collections

from . import element, errors


SimpleNovel = collections.namedtuple("SimpleNovel", "title genre words")


class NanoUser:

    __slots__ = ("client", "username", "_avatar", "_age", "_info", "_novels", "_simple_novel")

    def __init__(self, client, username):
        username = username.lower().replace(" ", "-")

        self.client = client
        self.username = username
        self._avatar = None
        self._age = None
        self._info = None
        self._novels = None

    @property
    async def avatar(self):
        if self._avatar is None:
            await self._initialize()
        return self._avatar

    @property
    async def age(self):
        if self._age is None:
            await self._initialize()
        return self._age

    @property
    async def info(self):
        if self._info is None:
            await self._initialize()
        return self._info

    @property
    async def novels(self):
        if self._novels is None:
            await self._init_novels()
        return self._novels

    @property
    async def current_novel(self):
        novels = await self.novels
        if not novels:
            return None
        return novels[0]

    @property
    async def simple_novel(self):
        if self._simple_novel is None:
            await self._initialize()
        return self._simple_novel

    async def _initialize(self):
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


class NanoInfo:

    __slots__ = ("bio", "lifetime_stats", "fact_sheet")

    def __init__(self, page):

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

    __slots__ = ("client", "id", "author", "year", "title", "genre", "cover", "winner", "synopsis", "stats", "_excerpt")

    def __init__(self, client, author, nid):
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
        if not self._excerpt:
            await self._initialize()
        return self._excerpt

    async def _initialize(self):
        page = await self.client.nano_get_page(f"participants/{self.author.username}/novels/{self.title}")
        if page is None:
            raise errors.NotANovel(self.title)

        self._excerpt = page.get_by_id("novel_excerpt").innerhtml


class NanoNovelStats:

    __slots__ = ("client", "novel", "daily_average", "target", "target_average", "total_today", "total",
                 "words_remaining", "current_day", "days_remaining", "finish_date", "average_to_finish")

    def __init__(self, client, novel):
        self.client = client
        self.novel = novel

    @property
    def author(self):
        return self.novel.author

    async def _initialize(self):
        page = await self.client.nano_get_page(f"participants/{self.author.username}/novels/{self.novel.title}/stats")
        # TODO
