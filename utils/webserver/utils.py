
import pathlib
import logging
import utils
import json
import ssl
import aiohttp.hdrs as hdrs
import aiohttp.web as web


log = logging.getLogger("utils.webserver")
log.setLevel(logging.INFO)
log.addHandler(logging.FileHandler(utils.log_folder / "webserver.log"))


def load_settings(file):
    """
        Load the settings file and parse it with JSON
    :param file: Location of the settings file
    :return: Dict result of parsing
    """
    with open(file, "r+") as file:
        data = json.load(file)
    return data


def apply_settings(app, settings):
    """
        From a dict of settings, save them locally and set up any necessary child systems from those settings
    :param app: aiohttp Application to add settings to
    :param settings: Dict of settings data
    """
    settings["base_path"] = pathlib.Path(settings["base_path"]).expanduser()
    app['settings'] = settings
    if "twitch_id" in settings:
        from .. import twitch
        cid = settings["twitch_id"]
        secret = settings["twitch_secret"]
        redirect = settings["twitch_redirect"]
        app['twitch_app'] = twitch.TwitchApp(cid=cid, secret=secret, redirect=redirect)


def setup_ssl(root, settings):
    """
        Create an SSL context from a given file root and settings dict
    :param root: Path root for the ssl directory
    :param settings: Webserver settings dictionary
    :return: New ssl context, or None if ssl settings aren't configured
    """
    out = None
    if settings["tokens"].get("ssl_cert"):
        out = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        cert = root / settings["tokens"]["ssl_cert"]
        key = root / settings["tokens"]["ssl_key"]
        out.load_cert_chain(cert, key)
    return out


def add_handler(app, handler, path=None):
    """
        Add a new handler to an application. Can be passed a type instead of an instance,
        and the handler will be automatically constructed.
    :param app: aiohttp Application to add handler to
    :param handler: Handler to add to the application
    :param path: Path for the handler to control, defaults to the root path
    """
    if isinstance(handler, type):
        handler = handler(app=app)

    routes = []
    for method in hdrs.METH_ALL:
        meth = getattr(handler, method.lower(), None)
        if meth is not None:
            npath = f"/{path}/{{tail:.*}}" if path else "/{tail:.*}"
            routes.append(web.route(method, npath, meth))
    app.add_routes(routes)


def add_handlers(app, handlers, paths=None):
    """
        Add a series of handlers to an application. Can be passed types instead of instances,
        and the handlers will be automatically constructed.
    :param app: aiohttp Application to add handlers to
    :param handlers: Handlers to add to the application
    :param paths: Paths that the handlers will control, defaults to root path
    """
    if paths is None:
        paths = ["" for _ in handlers]

    if len(paths) != len(handlers):
        raise ValueError("If supplied, length of paths list much match length of handlers list")

    for h, p in zip(handlers, paths):
        add_handler(app, h, p)


def setup(settings_path, handlers=None, paths=None):
    """
        Create and setup an application. One-off setup function for most people who don't
        need more advance customization.
    :param settings_path: Path to the settings file
    :param handlers: Handler instances or types to add to the application
    :param paths: Paths for the handlers to control
    :return: Newly setup Application instance
    """
    if paths is not None and handlers is None:
        raise ValueError("If paths is passed to setup, handlers must also be passed")

    app = web.Application()
    settings = load_settings(settings_path)
    apply_settings(app, settings)
    if handlers is not None:
        add_handlers(app, handlers, paths)
    return app
