

class User:

    __slots__ = ("id", "name", "display_name", "bio", "logo", "created_at", "updated_at", "type")

    def __init__(self, data):
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
        self.id = data["_id"]
        self.created_at = data["created_at"]
        self.sub_plan = data["sub_plan"]
        self.sub_plan_name = data["sub_plan_name"]
        self.is_gift = data["is_gift"]
        self.sender = data["sender"]
        self.user = User(data["user"])
