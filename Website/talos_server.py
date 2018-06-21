
import pathlib
import logging
import aiohttp.web as web

log = logging.getLogger("talosserver")
log.setLevel(logging.INFO)


HTML_PATH = pathlib.Path.home() / "public_html"


WEBMASTER_EMAIL = "talos.ptp@gmail.com"
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


class ServerError(Exception):
    pass


class TalosPrimaryHandler:

    async def site_get(self, request):
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

    async def api_post(self):
        log.info("API POST")
        return web.Response(text="Talos API Coming soon")

    async def get_path(self, path):
        # any hardcoded redirects here
        if path == "/":
            path = "/index"
        path = HTML_PATH.joinpath(path.lstrip("/"))

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
        return web.Response(text=BACKUP_ERROR.format(old_code, new_code, error, WEBMASTER_EMAIL), status=new_code)

    async def guess_mime(self, path):
        if KNOWN_MIMES.get(path.suffix):
            return KNOWN_MIMES[path.suffix]
        return "application/octet-stream"


def main():
    app = web.Application()
    handler = TalosPrimaryHandler()
    app.add_routes([
        web.get("/{tail:(?!api/).*}", handler.site_get),
        web.head("/{tail:(?!api/).*}", handler.do_head),
        web.get("/api/{tail:.*}", handler.api_get),
        web.post("/api/{tail:.*}", handler.api_post)
    ])
    web.run_app(app, port=80)


if __name__ == "__main__":
    main()
