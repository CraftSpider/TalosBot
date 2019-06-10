
import sys
import asyncio
import pathlib
import logging
import json
import ssl
import inspect
import warnings
import importlib.util
import importlib.machinery
import aiohttp.web as web
import website.handlers as handlers
import utils
import utils.twitch as twitch

log = logging.getLogger("talos.server")
log.setLevel(logging.INFO)
log.addHandler(logging.FileHandler(utils.log_folder / "server.log"))
importlib.machinery.SOURCE_SUFFIXES.append(".psp")


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


class TalosApplication(web.Application):
    """
        The custom application class used by Talos. Ignore the deprecation warnings unless they become errors,
        in which case yell at craft to fix things
    """

    def __init__(self, *args, **kwargs):
        """
            Initialize a new Talos Application. Just a passthrough to the super init
        :param args: Positional arguments
        :param kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)

    def apply_settings(self, settings):
        """
            From a dict of settings, save them locally and set up any necessary child systems from those settings
        :param settings: Dict of settings data
        """
        settings["base_path"] = pathlib.Path(settings["base_path"]).expanduser()

        self['settings'] = settings

        if "twitch_id" in settings:
            cid = settings["twitch_id"]
            secret = settings["twitch_secret"]
            redirect = settings["twitch_redirect"]
            self['twitch_app'] = twitch.TwitchApp(cid=cid, secret=secret, redirect=redirect)

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
        path = self["settings"]["base_path"] / path.lstrip("/")

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
        spec.loader.exec_module(psp)

        headers = dict()
        headers["Content-Type"] = "text/html"
        try:
            # Do argument resolution
            possible_args = {
                "app": self, "path": path, "dir": path.parent, "status": status, "request": request
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
            text=BACKUP_ERROR.format(first=old_code, second=new_code, err=error,
                                     email=self["settings"]["webmaster"]["email"]),
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

    app = TalosApplication()
    app.apply_settings(settings)

    site_handler = handlers.SiteHandler(app=app)
    auth_handler = handlers.AuthHandler(app=app)
    api_handler = handlers.APIHandler(app=app)

    app.add_routes([
        web.get("/{tail:(?!api/|auth/).*}", site_handler.get),
        web.head("/{tail:(?!api/|auth/).*}", site_handler.head),
        web.get("/api/{tail:.*}", api_handler.get),
        web.post("/api/{tail:.*}", api_handler.post),
        web.get("/auth/{tail:.*}", auth_handler.get)
    ])
    web.run_app(app, port=443 if sslcontext else 80, ssl_context=sslcontext)
    return 0


if __name__ == "__main__":
    sys.exit(main())
