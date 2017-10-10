
import irc.bot
import irc.events
import json
import urllib.request as urlreq

CLIENT_ID = "jt04pq09w3rui89eokt5ke2v1mveml"
CLIENT_SECRET = "0ca2smudgx2wavlu4o2al48lijjhy0"
URL_BASE = "https://api.twitch.tv/kraken"


def generate_user_token(client_ID, other_stuff):
    pass


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


class Talos(irc.bot.SingleServerIRCBot):
    def __init__(self, servers, nick, name):
        url = 'https://api.twitch.tv/kraken/users?login=' + "CraftSpider"
        headers = {'Client-ID': CLIENT_ID, 'Accept': 'application/vnd.twitchtv.v5+json'}
        request = urlreq.Request(url, headers=headers)
        r = json.loads(urlreq.urlopen(request).read().decode())
        self.channel_id = r['users'][0]['_id']

        super().__init__(servers, nick, name)
        self.reactor.add_global_handler("all_events", self.printer, 0)

    def printer(self, c, e):
        print(e)

    def on_pubmsg(self, c, e):
        pass

    def on_welcome(self, c, e):
        pass


token_data = generate_user_token(CLIENT_ID, CLIENT_SECRET)
token = token_data["access_token"]
password = "oauth:{}".format(token)
print(password)
twitch_server = irc.bot.ServerSpec("irc.chat.twitch.tv", password=password)

bot = Talos([twitch_server], "talosbot", "talosbot")
bot.start()

print(revoke_token(CLIENT_ID, token))
