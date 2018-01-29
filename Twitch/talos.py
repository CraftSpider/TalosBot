import json
import logging
import urllib.request as urlreq

import twitch_irc.bot as twirc

CLIENT_ID = "jt04pq09w3rui89eokt5ke2v1mveml"
CLIENT_SECRET = ""
URL_BASE = "https://api.twitch.tv/kraken"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("talos")


def generate_user_token(client_id, redirect="http://localhost"):
    url = "{}/oauth2/authorize?client_id={}&redirect_uri={}&response_type=token&scope=chat_login".format(
        URL_BASE, client_id, redirect
    )
    request = urlreq.Request(url, method="GET")
    request = urlreq.urlopen(request)
    result = request.geturl()
    print(result)
    return result


def generate_app_token(client_id, client_secret):
    url = "{}/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials&scope=chat_login".format(
        URL_BASE, client_id, client_secret
    )
    request = urlreq.Request(url, method="POST")
    request = urlreq.urlopen(request)
    result = request.read().decode()
    return json.loads(result)


def revoke_token(client_id, token):
    url = "{}/oauth2/revoke?client_id={}&token={}".format(URL_BASE, client_id, token)
    request = urlreq.Request(url, method="POST")
    request = urlreq.urlopen(request)
    result = request.status
    if result == 200:
        return True
    return False


class Talos(twirc.SingleServerBot):

    prefix = "^"

    def __init__(self, username, password, **params):
        super().__init__(self.prefix, username, password)

    def on_welcome(self, conn, event):
        log.info("| Talos Booting")
        log.info("| " + conn.ircname)
        log.info("| " + conn.server_address[0])
        conn.req_tags()
        conn.req_commands()
        conn.req_membership()
        conn.join("#rozoken")
        conn.join("#craftspider")
        conn.privmsg("#craftspider", "[Talos Boot successful]")
        log.info("Boot cycle complete")

    def on_all_raw_messages(self, conn, event):
        print(event)


def admin_only():

    def pred(ctx):
        return not ctx.tags.display_name == "CraftSpider"
    return twirc.check(pred)


if __name__ == "__main__":
    # token_data = generate_user_token(CLIENT_ID)
    bot_token = ""  # input("Token > ")  # token_data["access_token"]
    password = "oauth:{}".format(bot_token)

    bot = Talos("talos_bot_", password)

    @bot.command()
    @admin_only()
    def join(ctx, server):
        if server[0] != "#":
            server = "#" + server
        ctx.server.join(server)
        ctx.send("Joined channel " + server)

    @bot.command()
    @admin_only()
    def leave(ctx, channel):
        if channel[0] != "#":
            channel = "#" + channel
        if not bot.channels.get(channel):
            ctx.send("Talos not in channel " + channel)
            return
        ctx.server.part(channel)
        ctx.send("Left channel " + channel)

    # @bot.command()
    # def hello(ctx):
    #     ctx.send("Hello World!")

    bot.start()
