
import aiohttp.web as web


class HTTPSRedirecter:
    """
        Class that spins up a webserver that simply redirects all requests to the https version of the site
    """

    async def all(self, request: web.Request):
        """
            Handler for all requests
        :param request: Request to handle
        :return: HTTPFound
        """
        return web.HTTPFound(request.url.with_scheme("https"))


def main():
    """
        Main method for server redirector
    """
    app = web.Application()
    handler = HTTPSRedirecter()
    app.add_routes([
        web.get("/{tail:.*}", handler.all),
        web.post("/{tail:.*}", handler.all),
        web.head("/{tail:.*}", handler.all)
    ])
    web.run_app(app, port=80)


if __name__ == '__main__':
    main()
