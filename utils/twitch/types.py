
import datetime as dt
import json
import logging

from . import constants as const


log = logging.getLogger("talos.utils.twitch")


class OAuth:
    """
        Represent a Twitch OAuth user authentication
    """

    def __init__(self, data, app):
        """
            Initialize this OAuth object
        :param data: Initial OAuth data
        :param app: Associated Twitch application
        """
        self.app = app
        self._refresh_data(data)

    async def validate(self):
        """
            Check the validity of this OAuth object
        """
        headers = {
            "Authorization": f"OAuth {self.token}"
        }
        async with self.app.session.post(const.OAUTH + "validate", headers=headers) as response:
            validate = json.loads(await response.text())
            log.debug(validate)

    async def refresh(self):
        """
            Refresh this OAuth object, and update to new refreshed token
        :return: Whether refresh was successful
        """
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh,
            "client_id": self.app._cid,
            "client_secret": self.app._secret
        }
        async with self.app.session.post(const.OAUTH + "token", params=params) as response:
            refresh = json.loads(await response.text())
            if refresh.get("error") or refresh.get("status") >= 400:
                return False
            else:
                self._refresh_data(refresh)
                return True

    def _refresh_data(self, data):
        """
            Update the internal state with new refreshed data
        :param data: Dict of new data
        """
        self.token = data["access_token"]
        self._refresh = data["refresh_token"]
        self.expiration_time = data.get("expires_in", 3600)
        self.expires = dt.datetime.now() + dt.timedelta(seconds=self.expiration_time)
        self.scopes = set(data["scope"])
        self.type = data.get("token_type", "")


class User:
    """
        Represents a Twitch user, with name and associated data
    """

    __slots__ = ("id", "name", "display_name", "bio", "logo", "created_at", "updated_at", "type")

    def __init__(self, data):
        """
            Initialize twitch user object
        :param data: Initial data from Twitch API
        """
        self._refresh_data(data)

    def _refresh_data(self, data):
        """
            Update the internal state with new refreshed data
        :param data: Dict of new data
        """
        self.id = data["_id"]
        self.name = data["name"]
        self.display_name = data["display_name"]
        self.bio = data["bio"]
        self.logo = data["logo"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.type = data["type"]


class Subscription:
    """
        Represents a Twitch subscription with an associated User
    """

    __slots__ = ("id", "created_at", "sub_plan", "sub_plan_name", "is_gift", "sender", "user")

    def __init__(self, data):
        """
            Initialize twitch subscription object
        :param data:
        """
        self._refresh_data(data)

    def _refresh_data(self, data):
        """
            Update the internal state with new refreshed data
        :param data: Dict of new data
        """
        self.id = data["_id"]
        self.created_at = data["created_at"]
        self.sub_plan = data["sub_plan"]
        self.sub_plan_name = data["sub_plan_name"]
        self.is_gift = data["is_gift"]
        self.sender = data["sender"]
        self.user = User(data["user"])
