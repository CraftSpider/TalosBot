
import sys
import pathlib
import logging
import aiohttp.web as web
import spidertools.common as utils
import spidertools.webserver as webserver


log = logging.getLogger("talos.server")
log.setLevel(logging.INFO)
log.addHandler(logging.FileHandler(utils.log_folder / "server.log"))


SETTINGS_FILE = pathlib.Path(__file__).parent / "settings.json"


class TalosAPI(webserver.APIHandler):
    """
        Talos API handler class
    """

    async def on_commands(self, method, commands):
        """
            Handle a POST to the Talos Commands endpoint
        :param method: Method of the request
        :param commands: Commands data being passed in
        :return: Response, success or failure
        """
        return web.json_response(data={"error": "Talos Command posting is WIP"})


def main():
    """
        Main method for the Talos webserver. Sets up and runs the webserver
    :return: Exit code
    """

    app = webserver.setup(SETTINGS_FILE,
                          [TalosAPI, webserver.AuthHandler, webserver.SiteHandler],
                          ["api", "auth", ""])
    sslctx = webserver.setup_ssl(pathlib.Path(__file__).parent, app["settings"])
    web.run_app(app, port=443 if sslctx else 80, ssl_context=sslctx)
    return 0


if __name__ == "__main__":
    sys.exit(main())
