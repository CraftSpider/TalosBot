
import aiohttp
import io
import logging
import re

log = logging.getLogger("talos.utils")


class TalosHTTPClient(aiohttp.ClientSession):

    __slots__ = ("username", "password", "btn_key", "cat_key")

    NANO_URL = "https://nanowrimo.org/"
    BTN_URL = "https://www.behindthename.com/"
    CAT_URL = "https://thecatapi.com/api/"
    XKCD_URL = "https://xkcd.com/"

    def __init__(self, *args, **kwargs):
        """
            Create a Talos HTTP Client object
        :param args: arguments to pass on
        :param kwargs: keyword args to use and pass on
        """
        self.username = kwargs.pop("username", "")
        self.password = kwargs.pop("password", "")
        self.btn_key = kwargs.pop("btn_key", "")
        self.cat_key = kwargs.pop("cat_key", "")

        super().__init__(*args, **kwargs)

    async def get_site(self, url, **kwargs):
        """
            Get the text of a given URL
        :param url: url to get text from
        :param kwargs: keyword args to pass to the GET call
        :return: text of the requested page
        """
        async with self.get(url, **kwargs) as response:
            return await response.text()

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
                text = await response.text()
                return re.findall(r"<name>(.*?)</name>", text)
            else:
                log.warning("BTN returned {}".format(response.status))
                return None

    async def nano_get_user(self, username):
        """
            Returns a given NaNo user profile, if it can be found.
        :param username: username of nano user to get profile of
        :return: text of the profile page for that user or None
        """
        async with self.get(self.NANO_URL + "participants/{}".format(username)) as response:
            if response.status == 200:
                if not str(response.url).startswith("https://nanowrimo.org/participants"):
                    return None
                return await response.text()
            elif response.status == 403:
                response = await self.nano_login_client()
                log.debug("Login Status: {}".format(response))
                return await self.nano_get_user(username)
            else:
                print(response.status)
                return None

    async def nano_get_novel(self, username, novel_name=""):  # TODO: Convert to an HTML Parser
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
            novel_name = re.search(r"<a href=\"/participants/{}/novels/(.*?)/stats\">".format(username), user_page)
            if novel_name is None:
                return None, None
            novel_name = novel_name.group(1)
        # Get novel page for return
        async with self.get(self.NANO_URL + "participants/{}/novels/{}".format(username, novel_name)) as response:
            if response.status == 200:
                if not str(response.url).startswith("https://nanowrimo.org/participants"):
                    return None, None
                novel_page = await response.text()
            elif response.status == 403:
                response = await self.nano_login_client()
                log.debug("Login Status: {}".format(response))
                return await self.nano_get_novel(username, novel_name)
            elif response.status == 404:
                return None, None
            else:
                log.warning("Got unexpected response status {}".format(response.status))
                return None, None
        # Get novel stats for return
        async with self.get(self.NANO_URL + "participants/{}/novels/{}/stats".format(username, novel_name)) as response:
            if response.status == 200:
                if not str(response.url).startswith("https://nanowrimo.org/participants"):
                    return None, None
                novel_stats = await response.text()
            elif response.status == 403:
                response = await self.nano_login_client()
                log.debug("Login Status: {}".format(response))
                return await self.nano_get_novel(username, novel_name)
            elif response.status == 404:
                return None, None
            else:
                log.warning("Got unexpected response status {}".format(response.status))
                return None, None
        return novel_page, novel_stats

    async def nano_login_client(self):  # TODO: Convert to an HTML Parser, add tries before giving up
        """
            Login the client to the NaNo site.
        :return: status of login request.
        """
        login_page = await self.get_site(self.NANO_URL + "sign_in")
        pattern = re.compile("<input name=\"authenticity_token\" .*? value=\"(.*?)\" />")
        auth_key = pattern.search(login_page).group(1)
        params = {
            "utf8": "✓",
            "authenticity_token": auth_key,
            "user_session[name]": self.username,
            "user_session[password]": self.password,
            "user_session[remember_me]": "0",
            "commit": "Sign+in"
        }
        async with self.post(self.NANO_URL + "sign_in", data=params) as response:
            return response.status

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
            import json
            data = json.loads(data)
        async with self.get(data["img"]) as response:
            data["img_data"] = io.BytesIO(await response.read()), data["img"].split("/")[-1]
        return data
