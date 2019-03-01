
import aiohttp.web as web


class APIHandler:
    """
        Handler for the Talos Webserver API. Parses and dispatches requests, returning their result
    """

    __slots__ = ()

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
        :param data: Commands data being passed in
        :return: Response, success or failure
        """
        # TODO
        return web.Response(text="Talos Command posting is WIP")

