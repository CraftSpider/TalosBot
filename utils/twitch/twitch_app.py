
import aiohttp
import json
from . import types


BASE_URL = "https://api.twitch.tv/kraken/"


class TwitchApp:

    __slots__ = ("_cid", "_secret", "_redirect", "_oauths", "session", "_users")

    def __init__(self, cid, secret, redirect="http://localhost"):
        self._cid = cid
        self._secret = secret
        self._redirect = redirect
        self._oauths = {}
        self._users = {}
        self.session = None

    async def open(self):
        self.session = aiohttp.ClientSession()

    async def get_oauth(self, code):
        params = {
            "client_id": self._cid,
            "client_secret": self._secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self._redirect
        }
        async with self.session.post("https://id.twitch.tv/oauth2/token", params=params) as response:
            result = json.loads(await response.text())
            self._get_user_oauth(result)

    async def _get_user_oauth(self, oauth):
        headers = self.build_request_headers(oauth["access_token"])
        async with self.session.get(BASE_URL + "channel/", headers=headers) as response:
            result = json.loads(await response.text())
            self._oauths[result["name"]] = oauth

    async def get_user(self, name):
        user = self._users.get(name)
        if user is not None:
            return user
        async with self.session.get(BASE_URL + "users?login=" + name, headers=self.build_request_headers(name)) as response:
            result = json.loads(await response.text())
            user = types.User(result)
            self._users[user.name] = user
            return user

    def build_request_headers(self, name):
        return {
            "Accept": "application/vnd.twitchtv.v5+json",
            "Client-ID": self._cid,
            "Authorization": "OAuth " + (self._oauths[name] if self._oauths.get(name) is not None else name)
        }

    async def get_all_subs(self, name):
        user = await self.get_user(name)
        # TODO: request raised permissions if necessary
        total = None
        offset = 0
        out = []
        while total is None or offset < total:
            params = {
                "limit": 100,
                "offset": offset,
            }
            async with self.session.get(BASE_URL + f"channels/{user.id}/subscriptions",
                                        headers=self.build_request_headers(name),
                                        params=params) as response:
                result = json.loads(await response.text())
                total = result["_total"]
                out += map(lambda x: types.Subscription(x), result["subscriptions"])
            offset += 100
        return out

    async def close(self):
        await self.session.close()
