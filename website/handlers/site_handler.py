
import logging
import pathlib
import aiohttp.web as web


log = logging.getLogger("talos.server.site")


class SiteHandler:
    """
        Site handler class for Talos server. Contains handlers for GETs, POSTs, and such
    """

    def __init__(self, app):
        """
            Initializer for the Handler. Will only be run once due to singleton nature
        :param settings: Settings dict for the server
        """
        super().__init__()
        self.app = app
        self.webmaster = self.app["settings"].get("webmaster")
        self.base_path = self.app["settings"].get("base_path")

    # Request handlers

    async def get(self, request):
        """
            GET a page on the site normally
        :param request: aiohttp Request
        :return: Response object
        """
        log.info("Site GET")
        path = await self.app.get_path(request.path)
        if isinstance(path, int):
            response = await self.app.error_code(path)
        else:
            response = await self.app.get_response(path, request=request)
        return response

    async def head(self, request):
        """
            Respond to a HEAD request properly
        :param request: aiohttp Request
        :return: Response object
        """
        log.info("Site HEAD")
        response = await self.get(request)
        response = web.Response(headers=response.headers, status=response.status)
        return response
