
class TalosUser:

    __slots__ = ("database", "id", "description", "total_commands", "cur_title", "invoked_data", "titles", "options")

    def __init__(self, database, data):
        self.database = database

        profile_data = data.get("profile", [])
        self.id = profile_data[0]
        self.description = profile_data[1]
        self.total_commands = profile_data[2]
        self.cur_title = profile_data[3] or ""

        self.invoked_data = data["invoked"]

        self.titles = list(map(lambda x: x[0], data["titles"]))

        self.options = data["options"]

    def get_favorite_command(self):
        return self.invoked_data[len(self.invoked_data) - 1]

    def check_title(self, title):
        print(title, self.titles)
        if title in self.titles:
            return True
        return False

    def set_title(self, title):
        if self.check_title(title):
            self.database.set_title(self.id, title)
            return True
        return False

    def clear_title(self):
        self.database.set_title(self.id, None)


class UserOptions:

    __slots__ = ("database", "id", "rich_embeds", "prefix")

    def __init__(self, database, data):
        self.database = database

        self.id = data[0]
        self.rich_embeds = bool(data[1])
        self.prefix = data[2]


class GuildOptions:

    __slots__ = ("database", "id", "rich_embeds", "fail_message", "pm_help", "commands", "user_commands",
                 "joke_commands", "writing_prompts", "prompts_channel", "prefix", "timezone")

    def __init__(self, database, data):
        self.database = database

        self.id = data[0]
        i = 1
        for item in self.__slots__[2:]:
            option = data[i]
            if isinstance(option, int) and option == 1 or option == 0:
                option = bool(option)
            setattr(self, item, option)
            i += 1


class PermissionRule:

    __slots__ = ("database", "id", "command", "perm_type", "target", "priority", "allow")

    def __init__(self, database, data):
        self.database = database

        self.id = data[0]
        i = 1
        for item in self.__slots__[2:]:
            setattr(self, item, data[i])
            i += 1

    def __lt__(self, other):
        if isinstance(other, PermissionRule):
            return self.priority < other.priority

    def __gt__(self, other):
        if isinstance(other, PermissionRule):
            return self.priority > other.priority
