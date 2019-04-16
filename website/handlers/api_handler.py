
import json
import logging
import secrets
import aiohttp.web as web


log = logging.getLogger("talos.server.api")


class APIHandler:
    """
        Handler for the Talos Webserver API. Parses and dispatches requests, returning their result
    """

    __slots__ = ("app",)

    def __init__(self, app):
        super().__init__()
        self.app = app

    async def get(self, request):
        """
            GET a page from the API
        :param request: aiohttp Request
        :return: Response object
        """
        log.info("API GET")
        return web.Response(text="Talos API Coming soon")

    async def post(self, request):
        """
            POST to the Talos API
        :param request: aiohttp Request
        :return: Response object
        """
        log.info("API POST")
        headers = request.headers

        # Verify token
        user_token = headers.get("token")
        username = headers.get("username")
        server_token = self.app["settings"]["tokens"].get(username, None)
        if user_token is None or server_token is None:
            return web.Response(text="Invalid Token/Unknown User", status=403)
        known = secrets.compare_digest(user_token, server_token)
        if not known:
            return web.Response(text="Invalid Token/Unknown User", status=403)

        # And finally we can do what the request is asking
        try:
            path = "_".join(request.path.split("/")[1:])
            data = await request.json()
            return await self.dispatch(path, data)
        except json.JSONDecodeError:
            return web.Response(text="Malformed JSON in request", status=400)

    async def dispatch(self, path, data):
        """
            Dispatch an API command for a given path with given data
        :param path: API endpoint path
        :param data: Data sent to this endpoint
        :return: Web response to return
        """
        parser = getattr(self, "handle_" + path, None)
        if parser is not None:
            data = parser(data)

        handler = getattr(self, "on_" + path, None)
        if handler is not None:
            return await handler(data)
        else:
            return web.Response(text="Unknown API Command")

    async def on_commands(self, commands):
        """
            Handle a POST to the Talos Commands endpoint
        :param commands: Commands data being passed in
        :return: Response, success or failure
        """
        # TODO
        return web.Response(text="Talos Command posting is WIP")

