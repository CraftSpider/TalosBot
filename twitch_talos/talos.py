import json
import logging
import urllib.request as urlreq

# import airc
airc = None

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


# class Talos(airc.TwitchBot):
#
#     async def on_welcome(self, event):
#         log.info("| Talos Booting")
#         log.info("| " + event.server.username)
#         await self.server.req_tags()
#         await self.server.req_commands()
#         await self.server.req_membership()
#         await self.server.join("#craftspider")
#         await self.server.join("#alixrose99")
#         await self.server.privmsg("#craftspider", "[Talos Boot successful]")
#         log.info("Boot cycle complete")


def dev_only():

    def pred(ctx: airc.Context):
        return ctx.author.display_name == "CraftSpider"
    return airc.check(pred)


def channel_specific(channel):

    def pred(ctx: airc.Context):
        return ctx.channel.name == channel
    return airc.check(pred)


def main():
    with open("token.txt") as tokens:
        bot_token = tokens.read()

    # token_data = generate_user_token(CLIENT_ID)
    uri = "ws://irc-ws.chat.twitch.tv"
    password = "oauth:{}".format(bot_token)

    talos = Talos("^", user_type=airc.UserType.known_bot)

    @talos.command()
    @dev_only()
    async def join(ctx, channel):
        if channel[0] != "#":
            channel = "#" + channel
        await talos.server.join(channel)
        await ctx.send("Joined channel " + channel)

    @talos.command()
    @dev_only()
    async def leave(ctx, channel):
        if channel[0] != "#":
            channel = "#" + channel
        if not talos.get_channel(channel):
            ctx.send("Talos not in channel " + channel)
            return
        await talos.server.part(channel)
        await ctx.send("Left channel " + channel)

    @talos.command()
    async def wr(ctx):
        await ctx.send("Current WR is 29:14 by Lynx")

    @talos.command()
    @airc.mod_only()
    async def settitle(ctx: airc.Context, title):
        await ctx.send("Implementation soon" + title)

    talos.run(uri=uri, username="talos_bot_", password=password)


if __name__ == "__main__":
    main()
