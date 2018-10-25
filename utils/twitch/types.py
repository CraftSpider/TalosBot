import datetime as dt
import json

from . import constants as const


class OAuth:

    def __init__(self, data, app):
        self.app = app
        self._refresh_data(data)

    async def validate(self):
        headers = {
            "Authorization": f"OAuth {self.token}"
        }
        async with self.app.session.post(const.OAUTH + "validate", headers=headers) as response:
            validate = json.loads(await response.text())

    async def refresh(self):
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
        self.token = data["access_token"]
        self._refresh = data["refresh_token"]
        self.expiration_time = data.get("expires_in", 3600)
        self.expires = dt.datetime.now() + dt.timedelta(seconds=self.expiration_time)
        self.scopes = set(data["scope"])
        self.type = data.get("token_type", "")


class User:

    __slots__ = ("id", "name", "display_name", "bio", "logo", "created_at", "updated_at", "type")

    def __init__(self, data):
        self._refresh_data(data)

    def _refresh_data(self, data):
        self.id = data["_id"]
        self.name = data["name"]
        self.display_name = data["display_name"]
        self.bio = data["bio"]
        self.logo = data["logo"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.type = data["type"]


class Subscription:

    __slots__ = ("id", "created_at", "sub_plan", "sub_plan_name", "is_gift", "sender", "user")

    def __init__(self, data):
        self._refresh_data(data)

    def _refresh_data(self, data):
        self.id = data["_id"]
        self.created_at = data["created_at"]
        self.sub_plan = data["sub_plan"]
        self.sub_plan_name = data["sub_plan_name"]
        self.is_gift = data["is_gift"]
        self.sender = data["sender"]
        self.user = User(data["user"])
