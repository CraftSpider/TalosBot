
import asyncio
import pytest

import class_factories as dfacts
import talos as dtalos


dtalos.TOKEN_FILE = "../Discord/token.txt"


@pytest.fixture
def testlos():
    testlos = dtalos.Talos()
    testlos._connection = dfacts.get_state()
    yield testlos
    loop = asyncio.get_event_loop()
    loop.run_until_complete(testlos.close())


@pytest.fixture(scope="module")
def testlos_m(request):

    try:
        nano_login, btn_key, cat_key = dtalos.load_nano_login(), dtalos.load_btn_key(), dtalos.load_cat_key()
    except FileNotFoundError:
        nano_login, btn_key, cat_key = ["", ""], "", ""

    testlos = dtalos.Talos(nano_login=nano_login, btn_key=btn_key, cat_key=cat_key)
    testlos._connection = dfacts.get_state()
    testlos.load_extensions()
    request.module.testlos = testlos
    yield testlos
    loop = asyncio.get_event_loop()
    loop.run_until_complete(testlos.close())


@pytest.fixture(scope="module")
def loop():
    return asyncio.get_event_loop()
