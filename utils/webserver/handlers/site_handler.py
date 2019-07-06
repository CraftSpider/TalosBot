
import logging
import aiohttp.web as web

from .base_handler import BaseHandler


log = logging.getLogger("utils.webserver.site")


class SiteHandler(BaseHandler):
    """
        Site handler class for Talos server. Contains handlers for GETs, POSTs, and such
    """

    __slots__ = ("webmaster", "base_path")

    def __init__(self, app):
        """
            Initializer for the Handler. Will only be run once due to singleton nature
        :param app: Application for this server
        """
        super().__init__(app)
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
        path = await self.get_path(request.path)
        if isinstance(path, int):
            response = await self.error_code(path)
        else:
            response = await self.get_response(path, request=request)
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
