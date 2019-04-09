
import logging
import aiohttp.web as web
import utils.twitch as twitch

log = logging.getLogger("talos.server.auth")


class AuthHandler:

    __slots__ = ("app", "t_redirect")

    def __init__(self, app):
        super().__init__()
        self.app = app
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
