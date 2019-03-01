
import aiohttp.web as web


class APIHandler:

    __slots__ = ()

    async def dispatch(self, path, data):
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

