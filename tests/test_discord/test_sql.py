
import spidertools.discord.events as events
import discord_talos.talossql as data


def test_talos_admin():

    test_data = [1, 2]
    talosadmin = data.TalosAdmin(test_data)

    assert talosadmin.guild_id == 1
    assert talosadmin.user_id == 2
    assert talosadmin.to_row() == test_data
    assert talosadmin.table_name() == "admins"


def test_invoked_command():

    test_data = [2, "help", 100]
    invoked = data.InvokedCommand(test_data)

    assert invoked.id == 2
    assert invoked.command_name == "help"
    assert invoked.times_invoked == 100
    assert invoked.to_row() == test_data
    assert invoked.table_name() == "invoked_commands"


def test_user_title():

    test_data = [2, "test"]
    title = data.UserTitle(test_data)

    assert title.id == 2
    assert title.title == "test"
    assert title.to_row() == test_data
    assert title.table_name() == "user_titles"


def test_user_profile():

    test_data = [2, "a description", 250, "tester"]
    profile = data.UserProfile(test_data)

    assert profile.id == 2
    assert profile.description == "a description"
    assert profile.commands_invoked == 250
    assert profile.title == "tester"
    assert profile.to_row() == test_data
    assert profile.table_name() == "user_profiles"


def test_user_options():

    test_data = [2, 1, "^"]
    options = data.UserOptions(test_data)

    assert options.id == 2
    assert options.rich_embeds is True
    assert options.prefix == "^"
    assert options.to_row() == [2, True, "^"]
    assert options.table_name() == "user_options"


def test_talos_user():

    fav_command = data.InvokedCommand([2, "help", 100])

    test_data = {
        "profile": data.UserProfile([2, "a description", 250, "tester"]),
        "invoked": [fav_command, data.InvokedCommand([2, "info", 50])],
        "titles": [data.UserTitle([2, "tester"])],
        "options": data.UserOptions([2, 1, "^"])
    }

    user = data.TalosUser(test_data)

    assert user.id == user.profile.id
    assert user.title == user.profile.title
    assert len(user.removed_items()) == 0
    assert user.get_favorite_command() == fav_command

    assert user.check_title("testing") is False
    assert user.set_title("testing") is False
    assert user.title == "tester"
    user.add_title("testing")
    assert user.check_title("testing") is True
    assert user.set_title("testing") is True
    assert user.title == "testing"
    user.clear_title()
    assert user.title is None
    user.remove_title("testing")
    assert user.check_title("testing") is False
    assert user.set_title("testing") is False
    assert user.title is None

    assert len(user.removed_items()) == 1


def test_guild_options():

    test_data = [1, 1, 0, 0, 1, 1, 1, 0, 1, "prompts", 0, "mod_log", "^", "UTC"]
    options = data.GuildOptions(test_data)

    assert options.id == 1
    assert options.rich_embeds is True
    assert options.fail_message is False
    assert options.pm_help is False
    assert options.any_color is True
    assert options.commands is True
    assert options.user_commands is True
    assert options.joke_commands is False
    assert options.writing_prompts is True
    assert options.prompts_channel == "prompts"
    assert options.mod_log is False
    assert options.log_channel == "mod_log"
    assert options.prefix == "^"
    assert options.timezone == "UTC"


def test_permission_rule():

    test_data = [2, "nick", "channel", "general", 10, 1]
    perms = data.PermissionRule(test_data)

    assert perms.id == 2
    assert perms.command == "nick"
    assert perms.perm_type == "channel"
    assert perms.target == "general"
    assert perms.priority == 10
    assert perms.allow is True


def test_guild_command():

    test_data = [2, "test", "haha this is a test"]
    command = data.GuildCommand(test_data)

    assert command.id == 2
    assert command.name == "test"
    assert command.text == "haha this is a test"


def test_guild_event():

    test_data = [2, "test", "1d1h1m", 24, "general", "Hello World!"]
    event = data.GuildEvent(test_data)

    assert event.id == 2
    assert event.name == "test"
    assert event.period == events.EventPeriod("1d1h1m")
    assert event.last_active == 24
    assert event.channel == "general"
    assert event.text == "Hello World!"


def test_data_classes(database):
    options = data.UserOptions([2, 0, "^"])
    profile = data.TalosUser({"profile": data.UserProfile([1, "", 100, ""]),
                                     "invoked": {},
                                     "titles": [],
                                     "options": options})
    database.save_item(options)
    database.save_item(profile)

    assert options == database.get_item(data.UserOptions, id=2)
    assert profile == database.get_item(data.UserProfile, id=1)

    database.remove_item(options)
    database.remove_item(profile)

    assert database.get_item(data.UserOptions, id=2) is None
    assert database.get_item(data.UserProfile, id=1) is None


def test_talos_database(database):
    assert database.is_connected() is True, "Connected database considered not connected"
    assert database.commit() is True, "Database not committed despite existing"

    pass  # TODO test all the database functions
