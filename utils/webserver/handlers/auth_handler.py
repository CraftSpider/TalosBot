
import logging
import aiohttp.web as web
import utils.twitch as twitch

from .base_handler import BaseHandler

log = logging.getLogger("utils.webserver.auth")


class AuthHandler(BaseHandler):
    """
        Handler for the Twitch Webserver authorization path. Currently only handles twitch authorization,
        but any future auth flows will redirect here. Returns the authorization results
    """

    __slots__ = ("t_redirect",)

    def __init__(self, app):
        """
            Create a new Webserver Authorization handler
        :param app: The application this handler is tied to
        """
        super().__init__(app)
        self.t_redirect = None

    async def get(self, request):
        """
            GET the Twitch auth page
        :param request: aiohttp Request
        :return: Response object
        """
        log.info("Auth GET")
        tail = request.match_info['tail'].split("/")
        if tail[0] == "twitch":
            if tail[1] == "start":
                return await self.twitch_start(request)
            elif tail[1] == "complete":
                return await self.twitch_complete(request)
        else:
            return web.Response(text="Unrecognized authorization")

    async def twitch_start(self, request):
        """
            The beginning of a twitch Authorization request. Handles redirecting the user to twitch, and preparing
            for the redirect back afterwards
        :param request: aiohttp Request
        :return: Response object
        """
        self.t_redirect = request.query.get("redirect", None)
        try:
            twitch_app = self.app["twitch_app"]
            params = {
                "client_id": twitch_app.client_id,
                "redirect_uri": twitch_app.redirect,
                "response_type": "code",
                "scope": " ".join(request.query["scopes"].split(","))
            }
        except KeyError as er:
            return await self.app.error_code(500, er)
        return web.HTTPFound(twitch.OAUTH + "authorize?" + '&'.join(x + "=" + params[x] for x in params))

    async def twitch_complete(self, request):
        """
            The completion of a twitch Authorization request. Handles both the case of an error being found,
            or a correct authorization being finished
        :param request: aiohttp Request
        :return: Response object
        """
        if "error" in request.query:
            error = request.query["error"]
            description = request.query.get("error_description", "")
            text = f"""Error while authenticating to twitch: {error}\n\t{description}"""
            return web.Response(text=text)
        code = request.query["code"]
        await self.app['twitch_app'].get_oauth(code)
        if self.t_redirect is not None:
            redir = self.t_redirect
            self.t_redirect = None
            return web.HTTPFound(redir)
        return web.Response(text="All set!")
