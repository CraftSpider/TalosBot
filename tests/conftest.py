
import asyncio
import pathlib
import pytest
import logging
import io
import _pytest.python as py

import discord.ext.test as dpytest
import discord_talos.talos as dtalos
import discord_talos.talossql as sql


log = logging.getLogger("talos.tests.conftest")


class AsyncFunction(pytest.Function):

    def runtest(self):
        loop = asyncio.get_event_loop()
        testfunction = self.obj
        funcargs = self.funcargs
        testargs = {}
        for arg in self._fixtureinfo.argnames:
            testargs[arg] = funcargs[arg]
        loop.run_until_complete(testfunction(**testargs))
        return True


def pytest_pycollect_makeitem(collector, name, obj):
    if collector.istestfunction(obj, name) and asyncio.iscoroutinefunction(obj):
        module = collector.getparent(pytest.Module).obj
        clscol = collector.getparent(pytest.Class)
        cls = clscol and clscol.obj or None
        fm = collector.session._fixturemanager

        definition = py.FunctionDefinition(name=name, parent=collector, callobj=obj)
        fixinfo = fm.getfixtureinfo(definition, obj, cls)

        metafunc = py.Metafunc(definition, fixinfo, collector.config, cls=cls, module=module)

        if not metafunc._calls:
            return AsyncFunction(name, parent=collector, fixtureinfo=fixinfo)
        else:
            output = []
            for callspec in metafunc._calls:
                subname = f"{name}[{callspec.id}]"
                output.append(AsyncFunction(
                    name=subname,
                    parent=collector,
                    callspec=callspec,
                    callobj=obj,
                    fixtureinfo=fixinfo,
                    keywords={callspec.id: True},
                    originalname=name
                ))
            return output


@pytest.fixture()
def database(request):
    import json
    log.debug("Creating database connection")
    with open("discord_talos/schema.json") as f:
        schemadef = json.load(f)
    database = sql.TalosDatabase("localhost", 3306, "root", "", "talos_data", schemadef)
    database.verify_schema()
    if not database.is_connected():
        raise pytest.skip("Test database not found")
    if hasattr(request.module, "testlos"):
        request.module.testlos.database = database
    return database


@pytest.fixture()
def testlos():
    log.debug("Setting up Talos")
    tokens = dtalos.load_token_file(dtalos.TOKEN_FILE)
    testlos = dtalos.Talos(tokens=tokens)
    testlos.load_extensions(testlos.startup_extensions)
    dpytest.configure(testlos, 2, 2, 2)

    loop = testlos.loop
    loop.run_until_complete(testlos.init())

    yield testlos

    log.debug("Tearing down Talos")
    loop = testlos.loop
    loop.run_until_complete(testlos.close())


@pytest.fixture(scope="module")
def testlos_m(request):
    log.debug("Setting up Module Talos")
    tokens = dtalos.load_token_file(dtalos.TOKEN_FILE)
    testlos = dtalos.Talos(tokens=tokens)
    testlos.database.verify_schema()
    testlos.load_extensions(testlos.startup_extensions)
    dpytest.configure(testlos, 2, 2, 2)
    request.module.testlos = testlos

    loop = testlos.loop
    loop.run_until_complete(testlos.init())

    yield testlos

    log.debug("Tearing down Module Talos")
    loop = testlos.loop
    loop.run_until_complete(testlos.close())


@pytest.fixture(scope="module")
def loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def logcatch():
    return io.StringIO()


@pytest.fixture(scope="session", autouse=True)
def session_setup(logcatch):
    log.debug("Setting up test session")
    ensure_tokens()
    setup_logging(logcatch)


def setup_logging(logcatch):
    logging.root.handlers = []
    talos_log = logging.getLogger("talos")
    sh = logging.StreamHandler(logcatch)
    talos_log.addHandler(sh)
    talos_log.propagate = False
    talos_log.setLevel(logging.DEBUG)


def ensure_tokens():
    path = pathlib.Path(dtalos.TOKEN_FILE)
    if path.is_file():
        return
    dtalos.make_token_file(path)
