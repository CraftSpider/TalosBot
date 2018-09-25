
import aiohttp
import io
import logging
import re
import json
import datetime as dt
import utils.parsers as parse

log = logging.getLogger("talos.utils")


class TalosHTTPClient(aiohttp.ClientSession):

    __slots__ = ("nano_login", "btn_key", "cat_key", "nano_tries")

    NANO_URL = "https://nanowrimo.org/"
    BTN_URL = "https://www.behindthename.com/"
    CAT_URL = "https://thecatapi.com/api/"
    XKCD_URL = "https://xkcd.com/"
    SMBC_URL = "https://smbc-comics.com/"

    def __init__(self, *args, **kwargs):
        """
            Create a Talos HTTP Client object
        :param args: arguments to pass on
        :param kwargs: keyword args to use and pass on
        """
        self.nano_login = kwargs.pop("nano_login", "")
        self.btn_key = kwargs.pop("btn_key", "")
        self.cat_key = kwargs.pop("cat_key", "")
        self.nano_tries = 0

        super().__init__(*args, **kwargs)

    async def get_site(self, url, **kwargs):
        """
            Get the text of a given URL
        :param url: url to get text from
        :param kwargs: keyword args to pass to the GET call
        :return: text of the requested page
        """
        async with self.get(url, **kwargs) as response:
            return parse.to_dom(await response.text())

    async def btn_get_names(self, gender="", usage="", number=1, surname=False):
        """
            Get names from Behind The Name
        :param gender: gender to restrict names to. m or f
        :param usage: usage to restrict names to. eng for english, see documentation
        :param number: number of names to generate. Between 1 and 6.
        :param surname: whether to generate a random surname. Yes or No
        :return: List of names generated or None if failed
        """
        surname = "yes" if surname else "no"
        gender = "&gender="+gender if gender else gender
        usage = "&usage="+usage if usage else usage
        url = self.BTN_URL + "api/random.php?key={}&randomsurname={}&number={}{}{}".format(self.btn_key, surname,
                                                                                           number, gender, usage)
        async with self.get(url) as response:
            if response.status == 200:
                doc = parse.to_dom(await response.text())
                return [x.innertext for x in doc.get_by_tag("name")]
            else:
                log.warning("BTN returned {}".format(response.status))
                return None

    async def nano_get_page(self, url):
        """
            Safely gets a page from the NaNoWriMo website. Tries to log on, but returns None if that fails three times
            or for whatever reason the page can't be resolved
        :param url: NaNo URL path to fetch from
        :return: text of the page or None
        """
        async with self.get(self.NANO_URL + url) as response:
            if response.status == 200:
                if not str(response.url).startswith(self.NANO_URL + re.sub(r"/.*", "", url)):
                    return None
                return parse.to_dom(await response.text())
            elif response.status == 403:
                response = await self.nano_login_client()
                if response == 200:
                    return await self.nano_get_page(url)
                else:
                    return None
            else:
                log.warning(f"Got unexpected response status {response.status}")
                return None

    async def nano_get_user(self, username):
        """
            Returns a given NaNo user profile, if it can be found.
        :param username: username of nano user to get profile of
        :return: text of the profile page for that user or None
        """
        return await self.nano_get_page(f"participants/{username}")

    async def nano_get_novel(self, username, novel_name=""):
        """
            Returns the novel of a given NaNo user. This year's novel, if specific name not given.
        :param username: user to get novel of.
        :param novel_name: novel to get for user. Most recent if not given.
        :return: novel main page and novel stats page, or None None.
        """
        if novel_name == "":
            user_page = await self.nano_get_user(username)
            if user_page is None:
                return None, None
            try:
                navs = user_page.get_by_class("nav-tabs")[0]
                stats = user_page.get_by_tag("li", navs)[-1].first_child

                novel_name = re.search(f"/participants/{username}/novels/(.*?)/stats",
                                       stats.get_attribute("href")).group(1)
            except Exception as e:
                log.info("NaNo User not found, reason:")
                log.info(e)
                return None, None
        novel_page = await self.nano_get_page(f"participants/{username}/novels/{novel_name}")
        novel_stats = await self.nano_get_page(f"participants/{username}/novels/{novel_name}/stats")
        return novel_page, novel_stats

    async def nano_login_client(self):
        """
            Login the client to the NaNo site.
        :return: status of login request.
        """
        self.nano_tries += 1
        login_page = await self.get_site(self.NANO_URL + "sign_in")
        auth_el = login_page.get_by_name("authenticity_token")
        auth_key = ""
        if auth_el:
            auth_key = auth_el.get_attribute("value")
        params = {
            "utf8": "✓",
            "authenticity_token": auth_key,
            "user_session[name]": self.nano_login[0],
            "user_session[password]": self.nano_login[1],
            "user_session[remember_me]": "0",
            "commit": "Sign+in"
        }
        async with self.post(self.NANO_URL + "sign_in", data=params) as response:
            doc = parse.to_dom(await response.text())
            status = response.status
            sign_in = list(filter(lambda x: x.get_attribute("href") == "/sign_in", doc.get_by_tag("a")))
            if sign_in:
                if self.nano_tries < 3:
                    return await self.nano_login_client()
                else:
                    status = 403
                    self.nano_tries = 0
            else:
                self.nano_tries = 0
            return status

    async def get_cat_pic(self):
        """
            Get a random cat picture from The Cat API
        :return: A discord.File with a picture of a cat.
        """
        async with self.get(self.CAT_URL + "images/get?api_key={}&type=jpg,png".format(self.cat_key)) as response:
            filename = ""
            if response.content_type == "image/jpeg":
                filename = "cat.jpeg"
            elif response.content_type == "image/png":
                filename = "cat.png"
            picture_data = await response.read()
            if not picture_data:
                return self.get_cat_pic()
            file = io.BytesIO(picture_data), filename
        return file

    async def get_xkcd(self, xkcd):
        """
            Get the data from an XKCD comic and return it as a dict
        :param xkcd: XKCD to get, or None if current
        :return: Dict of JSON data
        """
        async with self.get(self.XKCD_URL + (f"{xkcd}/" if xkcd else "") + "info.0.json") as response:
            data = await response.text()
            data = json.loads(data)
        async with self.get(data["img"]) as response:
            data["img_data"] = io.BytesIO(await response.read()), data["img"].split("/")[-1]
        return data

    async def get_smbc_list(self):
        """
            Get the list of current SMBC comics from the smbc archive
        :return: List of elements
        """
        async with self.get(self.SMBC_URL + "comic/archive/") as response:
            dom = parse.to_dom(await response.text())
            selector = dom.get_by_name("comic")
            return selector.child_nodes[1:]

    async def get_smbc(self, smbc):
        """
            Get the data for an SMBC from its ID
        :param smbc: SMBC to get, or None if current
        :return: Dict of JSON data
        """
        data = {}
        async with self.get(self.SMBC_URL + f"comic/{smbc}", headers={"user-agent": ""}) as response:
            dom = parse.to_dom(await response.text())
            data["title"] = "-".join(dom.get_by_tag("title")[0].innertext.split("-")[1:]).strip()
            comic = dom.get_by_id("cc-comic")
            data["img"] = comic.get_attribute("src")
            data["alt"] = comic.get_attribute("title")
            time = dom.get_by_class("cc-publishtime")[0]
            date = dt.datetime.strptime(time.innertext, "Posted %B %d, %Y at %I:%M %p")
            data["time"] = date
        async with self.get(data["img"]) as response:
            data["img_data"] = io.BytesIO(await response.read()), data["img"].split("/")[-1]
        return data
