
import pytest

import utils as tutils


def test_empty_cursor():
    cursor = tutils.sql.EmptyCursor()

    with pytest.raises(StopIteration):
        cursor.__iter__().__next__()

    assert cursor.callproc("") is None, "callproc did something"
    assert cursor.close() is None, "close did something"
    assert cursor.execute("") is None, "execute did something"
    assert cursor.executemany("", []) is None, "executemany did something"

    assert cursor.fetchone() is None, "fetchone not None"
    assert cursor.fetchmany() == list(), "fetchmany not empty list"
    assert cursor.fetchall() == list(), "fetchall not empty list"

    assert cursor.description == tuple(), "description not empty tuple"
    assert cursor.rowcount == 0, "rowcount not 0"
    assert cursor.lastrowid is None, "lastrowid not None"


def test_data_classes(database):
    options = tutils.data.UserOptions([2, 0, "^"])
    profile = tutils.data.TalosUser({"profile": tutils.data.UserProfile([1, "", 100, ""]),
                                     "invoked": {},
                                     "titles": [],
                                     "options": options})
    database.save_item(options)
    database.save_item(profile)
    database.remove_item(options)
    database.remove_item(profile)


def test_empty_database():
    database = tutils.TalosDatabase("", -1, "notauser", "", "talos_data")

    assert database.is_connected() is False, "Empty database considered connected"
    assert database.raw_exec("SELECT * FROM admins") == list(), "raw_exec didn't return empty fetchall"
    assert database.commit() is False, "Database committed despite not existing?"

    pass  # TODO test all the database functions


def test_talos_database(database):
    if database.is_connected() is False:
        pytest.skip("Test database not found")

    assert database.is_connected() is True, "Connected database considered empty"
    assert database.commit() is True, "Database committed despite not existing?"

    pass  # TODO test all the database functions
