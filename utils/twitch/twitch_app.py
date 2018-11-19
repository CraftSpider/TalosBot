
import aiohttp
import json

from . import types, constants as const


class InsufficientPerms(Exception):

    def __init__(self, required, *args):
        self.required = required
        super().__init__(*args)


class NotASubscriber(Exception):
    pass


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
        if self.session is not None:
            await self.session.close()
        self.session = aiohttp.ClientSession()

    def build_request_headers(self, name):
        return {
            "Accept": "application/vnd.twitchtv.v5+json",
            "Client-ID": self._cid,
            "Authorization": "OAuth " + (self._oauths[name].token if self._oauths.get(name) is not None else name)
        }

    async def get_oauth(self, code):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        params = {
            "client_id": self._cid,
            "client_secret": self._secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self._redirect
        }
        async with self.session.post(const.OAUTH + "token", params=params) as response:
            result = json.loads(await response.text())
            oauth = types.OAuth(result, self)
            await self._get_user_oauth(oauth)

    async def _get_user_oauth(self, oauth):
        headers = self.build_request_headers(oauth.token)
        # TODO: requires channel read, figure out how to handle this
        async with self.session.get(const.KRAKEN + "channel/", headers=headers) as response:
            result = json.loads(await response.text())
            self._oauths[result["name"]] = oauth

    async def get_user(self, name):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        user = self._users.get(name)
        if user is not None:
            return user
        async with self.session.get(const.KRAKEN + "users?login=" + name,
                                    headers=self.build_request_headers(name)) as response:
            result = json.loads(await response.text())
            user = types.User(result["users"][0])
            self._users[user.name] = user
            return user

    async def get_all_subs(self, name):
        user = await self.get_user(name)
        total = None
        offset = 0
        out = []
        while total is None or offset < total:
            params = {
                "limit": 100,
                "offset": offset,
            }
            async with self.session.get(const.KRAKEN + f"channels/{user.id}/subscriptions",
                                        headers=self.build_request_headers(name),
                                        params=params) as response:
                result = json.loads(await response.text())
                if result.get("error") is not None:
                    with open("templog", "a") as file:
                        file.write(json.dumps(result))
                    if result.get("status") == 401:
                        raise InsufficientPerms("channel_subscriptions")
                    elif result.get("status") == 400:
                        raise NotASubscriber
                    raise Exception("Unkown error getting subscribers")
                total = result["_total"]
                out += map(lambda x: types.Subscription(x), result["subscriptions"])
            offset += 100
        return out

    async def close(self):
        await self.session.close()
