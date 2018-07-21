
import pathlib
import logging
import secrets
import json
import aiohttp
import aiohttp.web as web

log = logging.getLogger("talosserver")
log.setLevel(logging.INFO)


SETTINGS_FILE = pathlib.Path(__file__).parent / "settings.json"


BACKUP_ERROR = """
While attempting to handle HTTP code {0}, an unexpected error occured resulting in HTTP code {1}.

Error:
{2}

Please contact the webmaster at {3}.
"""
KNOWN_MIMES = {
    ".css": "text/css",
    ".html": "text/html",
    ".ico": "image/x-icon",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml"
}

counter = 0


class ServerError(Exception):
    pass


class TalosPrimaryHandler:

    _instance = None

    def __new__(cls, settings=None):

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, settings=None):
        if getattr(self, "_settings", None) is None:
            if settings is None:
                raise ServerError("Missing settings on server handler creation")
            self._settings = settings
            self.webmaster = self._settings.get("webmaster")
            self.base_path = pathlib.Path(self._settings.get("basepath")).expanduser()
            self.session = aiohttp.ClientSession()

    async def site_get(self, request):
        print(request.url)
        log.info("Site GET")
        path = await self.get_path(request.path)
        if isinstance(path, int):
            response = await self.error_code(path)
        else:
            response = await self.get_response(path)
        return response

    async def api_get(self, request):
        log.info("API GET")
        return web.Response(text="Talos API Coming soon")

    async def do_head(self, request):
        log.info("Site HEAD")
        response = await self.site_get(request)
        response = web.Response(headers=response.headers, status=response.status)
        return response

    async def api_post(self, request):
        log.info("API POST")
        path = request.path.lstrip("/").replace("/", "_")
        print(request.headers)
        try:
            data = await request.json()
            user_token = data.get("token")
            username = data.get("username")
            server_token = self._settings["tokens"].get(username)
            if user_token is None or server_token is None:
                return web.Response(text="Invalid Token/Unknown User", status=403)
            known = secrets.compare_digest(user_token, server_token)
            if not known:
                return web.Response(text="Invalid Token/Unknown User", status=403)
            # And finally we can do what the request is asking
            method = getattr(self, path, None)
            if method is not None:
                return await method(data)
        except json.JSONDecodeError:
            return web.Response(text="Malformed JSON in request", status=400)
        return web.Response(text="Talos API Coming soon")

    async def api_commands(self, data):
        
        return web.Response(text="Talos Command posting is WIP")

    async def auth_get(self, request):
        if len(request.query) > 0:
            code = request.query["code"]
            params = {
                "client_id": self._settings["twitch_id"],
                "client_secret": self._settings["twitch_secret"],
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self._settings["twitch_redirect"]
            }
            async with self.session.post("https://id.twitch.tv/oauth2/token", params=params) as response:
                result = json.loads(await response.text())
                print(result)
            return web.Response(text="All set!")
        params = {
            "client_id": self._settings["twitch_id"],
            "redirect_uri": self._settings["twitch_redirect"],
            "response_type": "code",
            "scope": "channel_subscriptions"
        }
        return web.HTTPFound("https://id.twitch.tv/oauth2/authorize?" + '&'.join(x + "=" + params[x] for x in params))

    async def get_path(self, path):
        # any hardcoded redirects here
        if path == "/":
            path = "/index"
        path = self.base_path.joinpath(path.lstrip("/"))

        # Now do logic to find the desired file. If found, return that path. If not, return an error code
        if pathlib.Path.is_file(path):
            return path
        elif pathlib.Path.is_dir(path):
            path = path / 'index.html'
            print(path.with_name(str(path.parent.name) + ".html"))
            if path.is_file():
                return path
            path = path.with_name(str(path.parent.name) + ".html")
            if path.is_file():
                return path
            else:
                return 404
        elif path.with_suffix(".html").is_file():
            return path.with_suffix(".html")
        else:
            return 404

    async def get_response(self, path, status=200):
        headers = dict()
        headers["Content-Type"] = await self.guess_mime(path)
        return web.FileResponse(path=path, status=status, headers=headers)

    async def error_code(self, status):
        path = await self.get_path(f"{status}.html")
        try:
            if isinstance(path, int):
                raise ServerError("Could not find specified error handler")
            return web.FileResponse(path, status=status)
        except Exception as e:
            return await self.backup_error_code(status, path, e)

    async def backup_error_code(self, old_code, new_code, error=None):
        return web.Response(text=BACKUP_ERROR.format(old_code, new_code, error, self.webmaster["email"]),
                            status=new_code)

    async def guess_mime(self, path):
        if KNOWN_MIMES.get(path.suffix):
            return KNOWN_MIMES[path.suffix]
        return "application/octet-stream"


def load_settings():
    with open(SETTINGS_FILE, "r+") as file:
        import json
        data = json.load(file)
    return data


def main():
    settings = load_settings()
    app = web.Application()
    handler = TalosPrimaryHandler(settings)
    app.add_routes([
        web.get("/{tail:(?!api/|auth/).*}", handler.site_get),
        web.head("/{tail:(?!api/|auth/).*}", handler.do_head),
        web.get("/api/{tail:.*}", handler.api_get),
        web.post("/api/{tail:.*}", handler.api_post),
        web.get("/auth/{tail:.*}", handler.auth_get)
    ])
    web.run_app(app, port=80)
    return 0


if __name__ == "__main__":
    main()
