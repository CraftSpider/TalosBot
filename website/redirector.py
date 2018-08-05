
import aiohttp.web as web


class HTTPSRedirecter:

    async def all(self, request):
        return web.HTTPFound("https://talosbot.org/" + request.path[1:])


def main():
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
