import json
import logging
import urllib.request as urlreq

import Twitch.twitch_irc.bot as twirc
import irc.events
import irc.bot

CLIENT_ID = "jt04pq09w3rui89eokt5ke2v1mveml"
CLIENT_SECRET = ""
URL_BASE = "https://api.twitch.tv/kraken"

logging.basicConfig(level=logging.DEBUG)
logging = logging.getLogger("talos")

def generate_user_token(client_ID, redirect="http://localhost"):
    url = "{}/oauth2/authorize?client_id={}&redirect_uri={}&response_type=token&scope=chat_login".format(URL_BASE, client_ID, redirect)
    request = urlreq.Request(url, method="GET")
    request = urlreq.urlopen(request)
    result = request.geturl()
    print(result)
    return result


def generate_app_token(client_ID, client_secret):
    url = "{}/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials&scope=chat_login".format(URL_BASE, client_ID, client_secret)
    request = urlreq.Request(url, method="POST")
    request = urlreq.urlopen(request)
    result = request.read().decode()
    return json.loads(result)


def revoke_token(client_ID, token):
    url = "{}/oauth2/revoke?client_id={}&token={}".format(URL_BASE, client_ID, token)
    request = urlreq.Request(url, method="POST")
    request = urlreq.urlopen(request)
    result = request.status
    if result == 200:
        return True
    return False


class Talos(twirc.SingleServerBot):

    prefix = "^"

    def __init__(self, servers, nick, name):
        super().__init__(self.prefix, servers, nick, name)

    def on_welcome(self, conn, event):
        conn.req_tags()
        conn.req_commands()
        conn.send_raw("JOIN #craftspider")
        conn.send_raw("PRIVMSG #craftspider :[Talos Boot successful]")


if __name__ == "__main__":
    # token_data = generate_user_token(CLIENT_ID)
    bot_token = ""  # input("Token > ")  # token_data["access_token"]
    password = "oauth:{}".format(bot_token)
    twitch_server = irc.bot.ServerSpec("irc.chat.twitch.tv", password=password)

    bot = Talos([twitch_server], "talos_bot_", "talos_bot_")

    @bot.command()
    def test(ctx):
        ctx.send("Hello World!")

    bot.start()

    # print(revoke_token(CLIENT_ID, bot_token))
