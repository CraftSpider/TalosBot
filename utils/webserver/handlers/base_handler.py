
import pathlib
import logging
import aiohttp.web as web
import importlib.machinery
import importlib.util
import asyncio
import warnings
import inspect
import os

from .errors import ServerWarning, ServerError


log = logging.getLogger("utils.webserver.handler")


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


def _module_from_file(path, base=None):
    """
        Create a python module from a file path
    :param path: Path to the file
    :param base: Base path for packages
    :return: New module object
    """
    temp = path.with_suffix("")
    if base is None:
        name = temp.name
    else:
        temp = temp.relative_to(base)
        name = ".".join(temp.parts)
    loader = importlib.machinery.SourceFileLoader(name, path.__fspath__())
    spec = importlib.util.spec_from_file_location(name, path, loader=loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _resolve_args(func, possible):
    """
        Resolve arguments for the signature of a given function
    :param func: Function to resolve
    :param possible: Possible arg names to the objects to pass
    :return: tuple of (args, kwargs) to call func with
    """
    signature = inspect.signature(func)
    args = []
    kwargs = {}
    for name in signature.parameters:
        param = signature.parameters[name]
        val = possible.get(name)
        if val is None:
            warnings.warn("Invalid PSP argument", ServerWarning)
        if param.kind == param.POSITIONAL_ONLY or param.kind == param.POSITIONAL_OR_KEYWORD:
            args.append(val)
        elif param.kind == param.KEYWORD_ONLY:
            kwargs[name] = val
        else:
            warnings.warn("PSP does not support * or ** parameters", ServerWarning)
    return args, kwargs


class BaseHandler:
    """
        Base class for all webserver handlers. Provides some useful methods, and other initialization
    """

    __slots__ = ("app",)

    def __init__(self, app):
        """
            Initialize a new handler object from an application
        :param app: Application tied to this handler
        """
        self.app = app

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
        path = self.app["settings"]["base_path"] / path.lstrip("/")

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

    async def guess_mime(self, path):
        """
            Guess the MIME type of a given path. If it isn't known, default to octet-stream
        :param path: Relative path to the desired file
        :return: MIME type best guess
        """
        if KNOWN_MIMES.get(path.suffix):
            return KNOWN_MIMES[path.suffix]
        return "application/octet-stream"

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
                                     email=self.app["settings"]["webmaster"]["email"]),
            status=new_code
        )

    async def python_page(self, path, status=200, *, request=None):
        """
            Takes in a path to a .psp file
            Runs the .psp and returns the result
        :param path: Path to .psp file to run
        :param status: status code, if we want to set a non-standard one.
        :param request: web.Request object
        :return: web.Response to send to the user
        """
        from .api_handler import APIHandler
        psp = _module_from_file(path)

        if not hasattr(psp, "page"):
            log.error("PSP file missing 'page' attribute")
            return await self.error_code(500, ServerError("Invalid PSP File"))
        if not inspect.isroutine(psp.page):
            log.error("PSP file 'page' attribute not a callable routine")
            return await self.error_code(500, ServerError("Invalid PSP File"))

        headers = dict()
        headers["Content-Type"] = "text/html"

        # Do argument resolution
        possible_args = {
            "app": self.app, "path": path, "dir": path.parent, "status": status, "request": request,
            "handler": self
        }
        for handler in self.app["handlers"]:
            if isinstance(handler, APIHandler):
                possible_args["api"] = handler
        args, kwargs = _resolve_args(psp.page, possible_args)

        curdir = os.getcwd()
        try:
            # Get result of page call
            os.chdir(self.app["settings"]["base_path"])
            if asyncio.iscoroutinefunction(psp.page):
                resp = await psp.page(*args, **kwargs)
            else:
                resp = psp.page(*args, **kwargs)
        except Exception as e:
            log.error(f"Encountered {e.__class__.__name__}: {e} while attempting to load page {path}")
            return await self.error_code(500, e)
        finally:
            os.chdir(curdir)
            del psp

        # Depending on result type, generate a response
        if resp is None:
            return await self.error_code(500, ServerError("PSP didn't return a value"))
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
