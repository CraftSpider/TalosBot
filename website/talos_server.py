
import sys
import asyncio
import pathlib
import logging
import secrets
import json
import ssl
import inspect
import warnings
import importlib.util
import aiohttp.web as web
import utils.twitch as twitch

log = logging.getLogger("talosserver")
log.setLevel(logging.INFO)


SETTINGS_FILE = pathlib.Path(__file__).parent / "settings.json"


BACKUP_ERROR = """
While attempting to handle HTTP code {first}, an unexpected error occured resulting in HTTP code {second}.

Original Error:
{err}

Please contact the webmaster at {email}.
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
    """
        Base error class for the Talos server
    """
    pass


class ServerWarning(Warning):
    """
        Base warning class for the Talos server
    """
    pass


class TalosPrimaryHandler:
    """
        Handler class for Talos server. Contains handlers for GETs, POSTs, and such
    """

    _instance = None

    def __new__(cls, settings=None):
        """
            Create new instance, Handler is a singleton so only every creates one instance
        :param settings: Settings dict for the server
        :return: Instance of Handler
        """

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, settings=None):
        """
            Initializer for the Handler. Will only be run once due to singleton nature
        :param settings: Settings dict for the server
        """
        if getattr(self, "_settings", None) is None:
            if settings is None:
                raise ServerError("Missing settings on server handler creation")
            self._settings = settings
            self.webmaster = self._settings.get("webmaster")
            self.base_path = pathlib.Path(self._settings.get("basepath")).expanduser()
            if self._settings.get("twitch_id") is None:
                self.twitch_app = None
                return
            self.twitch_app = twitch.TwitchApp(cid=self._settings["twitch_id"],
                                               secret=self._settings["twitch_secret"],
                                               redirect=self._settings["twitch_redirect"])
            self.t_redirect = None

    # Request handlers

    async def site_get(self, request):
        """
            GET a page on the site normally
        :param request: aiohttp Request
        :return: Response object
        """
        log.info("Site GET")
        path = await self.get_path(request.path)
        if isinstance(path, int):
            response = await self.error_code(path)
        else:
            response = await self.get_response(path, request=request)
        return response

    async def api_get(self, request):
        """
            GET a page from the API
        :param request: aiohttp Request
        :return: Response object
        """
        log.info("API GET")
        return web.Response(text="Talos API Coming soon")

    async def auth_get(self, request):
        """
            GET the Twitch auth page
        :param request: aiohttp Request
        :return: Response object
        """
        if request.query.get("code") is not None:
            code = request.query["code"]
            await self.twitch_app.get_oauth(code)
            if self.t_redirect is not None:
                redir = self.t_redirect
                self.t_redirect = None
                return web.HTTPFound(redir)
            return web.Response(text="All set!")
        self.t_redirect = request.query.get("redirect", None)
        try:
            params = {
                "client_id": self._settings["twitch_id"],
                "redirect_uri": self._settings["twitch_redirect"],
                "response_type": "code",
                "scope": " ".join(request.query["scopes"].split(","))
            }
        except KeyError as er:
            return await self.error_code(500, er)
        return web.HTTPFound("https://id.twitch.tv/oauth2/authorize?" + '&'.join(x + "=" + params[x] for x in params))

    async def do_head(self, request):
        """
            Respond to a HEAD request properly
        :param request: aiohttp Request
        :return: Response object
        """
        log.info("Site HEAD")
        response = await self.site_get(request)
        response = web.Response(headers=response.headers, status=response.status)
        return response

    async def api_post(self, request):
        """
            POST to the Talos API
        :param request: aiohttp Request
        :return: Response object
        """
        log.info("API POST")
        path = request.path.lstrip("/").replace("/", "_")
        print(request.headers)
        try:
            headers = request.headers
            data = await request.json()
            user_token = headers.get("token")
            username = headers.get("username")
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

    # API Methods

    async def api_commands(self, data):
        """
            Handle a POST to the Talos Commands endpoint
        :param data: Commands data being passed in
        :return: Response, success or failure
        """
        # TODO
        return web.Response(text="Talos Command posting is WIP")

    # Website Methods

    async def get_path(self, path):
        """
            Resolves a string path from a GET request to a path on the file system
            Does safety checks to make sure they're not getting something forbidden
        :param path: String path to reolve
        :return: Path object resolved, or an int representing status code
        """
        # any hardcoded redirects here
        if path == "/":
            path = "/index"
        path = self.base_path / path.lstrip("/")

        # Now do logic to find the desired file. If found, return that path. If not, return an error code
        if pathlib.Path.is_file(path):
            return path
        elif pathlib.Path.is_dir(path):
            # Look for an index.html, if that's missing, look for [dirname].html, if that's missing 404
            if (path / 'index.html').is_file():
                return path / 'index.html'
            elif (path / (str(path.name) + ".html")).is_file():
                return path / (str(path.name) + ".html")
            else:
                return 404
        elif path.with_suffix(".html").is_file():
            return path.with_suffix(".html")
        else:
            return 404

    async def get_response(self, path, status=200, *, request=None):
        """
            Takes in a Path object guaranteed to be a file on disk.
            If it's a dynamic page type, we run it and return that
            Otherwise we just respond with the path itself.
        :param path: Path to file to respond with
        :param status: status code, if we want to set a non-standard one.
        :param request: web.Request object
        :return: web.Response to send to the user
        """
        if path.suffix == ".psp":
            return await self.python_page(path, status, request=request)
        headers = dict()
        headers["Content-Type"] = await self.guess_mime(path)
        return web.FileResponse(path=path, status=status, headers=headers)

    async def python_page(self, path, status=200, *, request=None):
        """
            Takes in a path to a .psp file
            Runs the .psp and returns the result
        :param path: Path to .psp file to run
        :param status: status code, if we want to set a non-standard one.
        :param request: web.Request object
        :return: web.Response to send to the user
        """
        spec = importlib.util.spec_from_file_location("psp", path)
        psp = importlib.util.module_from_spec(spec)
        # loader = importlib.machinery.SourceFileLoader("psp", path.__fspath__())
        # psp = types.ModuleType(loader.name)
        headers = dict()
        headers["Content-Type"] = "text/html"
        try:
            # Do argument resolution
            possible_args = {
                "handler": self, "path": path, "dir": path.parent, "status": status, "request": request
            }
            argspec = inspect.getfullargspec(psp.page)
            args = []
            kwargs = {}
            for arg in argspec.args:
                val = possible_args.get(arg)
                if val is None:
                    warnings.warn("Invalid PSP argument", ServerWarning)
                args.append(val)

            # Get result of page call
            if asyncio.iscoroutinefunction(psp.page):
                resp = await psp.page(*args, **kwargs)
            else:
                resp = psp.page(*args, **kwargs)

            # Depending on result type, generate a response
            if isinstance(resp, int):
                return await self.error_code(resp)
            elif isinstance(resp, str):
                return web.Response(text=resp, status=status, headers=headers)
            elif isinstance(resp, dict):
                if resp.get("status") is None:
                    resp["status"] = status
                if resp.get("headers") is None:
                    resp["headers"] = headers
                return web.Response(**resp)
            else:
                return resp
        except Exception as e:
            log.error(f"Encountered {e} while attempting to load page {path}")
            return await self.error_code(500, e)
        finally:
            del psp

    async def error_code(self, status, error=None):
        """
            Takes in an error code and returns the relevant handler page
        :param status: Status code being thrown out
        :param error: Error that goes along with it, if relevant
        :return: web.Response object
        """
        path = await self.get_path(f"{status}.html")
        if isinstance(path, int):
            return await self.backup_error_code(status, path, error)
        return web.FileResponse(path, status=status)

    async def backup_error_code(self, old_code, new_code, error=None):
        """
            Called if error_code can't find a handler. Returns the default handler.
        :param old_code: Original code being thrown
        :param new_code: Code thrown from the error handler
        :param error: Error that goes along with code, if relevant
        :return: web.Response object
        """
        return web.Response(
            text=BACKUP_ERROR.format(first=old_code, second=new_code, err=error, email=self.webmaster["email"]),
            status=new_code
        )

    async def guess_mime(self, path):
        """
            Guess the MIME type of a given path. If it isn't known, default to octet-stream
        :param path: Relative path to the desired file
        :return: MIME type best guess
        """
        if KNOWN_MIMES.get(path.suffix):
            return KNOWN_MIMES[path.suffix]
        return "application/octet-stream"


def load_settings():
    """
        Load the settings file and parse it with JSON
    :return: Dict result of parsing
    """
    with open(SETTINGS_FILE, "r+") as file:
        data = json.load(file)
    return data


def main():
    """
        Main method for the Talos webserver. Sets up and runs the webserver
    :return: Exit code
    """
    settings = load_settings()

    if settings["tokens"].get("ssl_cert"):
        sslcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        cert = pathlib.Path(__file__).parent / settings["tokens"]["ssl_cert"]
        key = pathlib.Path(__file__).parent / settings["tokens"]["ssl_key"]
        sslcontext.load_cert_chain(cert, key)
    else:
        sslcontext = None

    app = web.Application()
    handler = TalosPrimaryHandler(settings)
    app.add_routes([
        web.get("/{tail:(?!api/|auth/).*}", handler.site_get),
        web.head("/{tail:(?!api/|auth/).*}", handler.do_head),
        web.get("/api/{tail:.*}", handler.api_get),
        web.post("/api/{tail:.*}", handler.api_post),
        web.get("/auth/{tail:.*}", handler.auth_get)
    ])
    web.run_app(app, port=443 if sslcontext else 80, ssl_context=sslcontext)
    return 0


if __name__ == "__main__":
    sys.exit(main())
