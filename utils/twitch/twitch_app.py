
import aiohttp
import json

from . import types, constants as const


class InsufficientPerms(Exception):
    """
        Raised when an operation is performed and the application is missing the required permissions
    """

    def __init__(self, required, *args):
        """
            Initialize new exception object
        :param required: Permission that is missing
        :param args: Associated message
        """
        self.required = required
        super().__init__(*args)


class NotASubscriber(Exception):
    """
        Raised when a User is not a subscriber to the current Streamer
    """


class TwitchApp:
    """
        Represents a twitch application
    """

    __slots__ = ("_cid", "_secret", "_redirect", "_oauths", "session", "_users")

    def __init__(self, cid, secret, redirect="http://localhost"):
        """
            Initialize Twitch application
        :param cid: Application ID
        :param secret: Application Secret
        :param redirect: Redirect URL for use in authentication
        """
        if not isinstance(cid, (str, bytes)):
            raise TypeError("Client ID must be string or bytes like object")
        if not isinstance(secret, (str, bytes)):
            raise TypeError("Client Secret must be string or bytes like object")

        self._cid = cid
        self._secret = secret
        self._redirect = redirect
        self._oauths = {}
        self._users = {}
        self.session = None

    @property
    def client_id(self):
        return self._cid

    @property
    def redirect(self):
        return self._redirect

    async def open(self):
        """
            Open a new application ClientSession
        """
        if self.session is not None:
            await self.session.close()
        self.session = aiohttp.ClientSession()

    def _get_token(self, name):
        oauth = self._oauths.get(name, None)
        if oauth is not None:
            oauth = oauth.token
        else:
            oauth = name
        return oauth

    def build_v5_headers(self, name):
        """
            Build the request headers for a Twitch v5 API request
        :param name: Name of the user to oauth with
        :return: Dict of request headers
        """
        return {
            "Accept": "application/vnd.twitchtv.v5+json",
            "Client-ID": self._cid,
            "Authorization": f"OAuth {self._get_token(name)}"
        }

    def build_helix_headers(self, name=None):
        if name is not None:
            return {
                "Authorization": f"Bearer {self._get_token(name)}"
            }
        else:
            return {
                "Client-ID": self._cid
            }

    async def get_oauth(self, code):
        """
            Get the OAuth data with the code given to us by twitch
        :param code: OAuth flow code returned by twitch
        """
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
        """
            Get the user associated with a new OAuth and save the OAuth in the internal state
        :param oauth: OAuth to get associated user
        """
        headers = self.build_helix_headers(oauth.token)
        async with self.session.get(const.HELIX + "users", headers=headers) as response:
            result = json.loads(await response.text())
            data = result["data"]
            for item in data:
                self._oauths[item["login"]] = oauth

    async def get_user(self, name):
        """
            Get the Twitch User associated with a given name
        :param name: Name of the twitch User to get
        :return: Twitch User
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
        user = self._users.get(name)
        if user is not None:
            return user
        async with self.session.get(const.KRAKEN + "users?login=" + name,
                                    headers=self.build_v5_headers(name)) as response:
            result = json.loads(await response.text())
            user = types.User(result["users"][0])
            self._users[user.name] = user
            return user

    async def get_all_subs(self, name):
        """
            Get all the subscribers for a given username
        :param name: Name of the user to get subs of
        :return: List of Subscribers to the given user
        """
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
                                        headers=self.build_v5_headers(name),
                                        params=params) as response:
                result = json.loads(await response.text())
                if result.get("error") is not None:
                    with open("templog", "a") as file:
                        file.write(json.dumps(result))
                    if result.get("status") == 401:
                        raise InsufficientPerms("channel_subscriptions")
                    elif result.get("status") == 400:
                        raise NotASubscriber()
                    raise Exception("Unkown error getting subscribers")
                total = result["_total"]
                out += map(lambda x: types.Subscription(x), result["subscriptions"])
            offset += 100
        return out

    async def close(self):
        """
            Close the current ClientSession and shutdown the application
        """
        await self.session.close()
