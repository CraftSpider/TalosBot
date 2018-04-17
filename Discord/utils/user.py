
class TalosUser:

    __slots__ = ("id", "description", "total_commands", "cur_title", "invoked_data", "titles")

    def __init__(self, data):

        profile_data = data.get("profile", [])
        self.id = profile_data[0]
        self.description = profile_data[1]
        self.total_commands = profile_data[2]
        self.cur_title = profile_data[3] or ""

        self.invoked_data = data["invoked"]

        self.titles = data["titles"]

    def get_favorite_command(self):
        return self.invoked_data[len(self.invoked_data) - 1]
