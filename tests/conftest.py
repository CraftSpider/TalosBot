
import asyncio
import pathlib
import pytest

import class_factories as dfacts
import talos as dtalos
import utils as tutils


@pytest.fixture()
def database():
    database = tutils.TalosDatabase("localhost", "3306", "root", "", "")
    database.verify_schema()
    return database


@pytest.fixture
def testlos():
    tokens = dtalos.load_token_file(dtalos.TOKEN_FILE)
    testlos = dtalos.Talos(tokens=tokens)
    testlos._connection = dfacts.get_state()
    testlos.load_extensions()
    yield testlos
    loop = asyncio.get_event_loop()
    loop.run_until_complete(testlos.close())


@pytest.fixture(scope="module")
def testlos_m(request):
    tokens = dtalos.load_token_file(dtalos.TOKEN_FILE)
    testlos = dtalos.Talos(tokens=tokens)
    testlos._connection = dfacts.get_state()
    testlos.load_extensions()
    request.module.testlos = testlos
    yield testlos
    loop = asyncio.get_event_loop()
    loop.run_until_complete(testlos.close())


@pytest.fixture(scope="module")
def loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session", autouse=True)
def ensure_tokens():
    path = pathlib.Path(dtalos.TOKEN_FILE)
    if path.is_file():
        return
    dtalos.make_token_file(path)
