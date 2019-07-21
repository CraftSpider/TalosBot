"""
    Tests Talos utils. Ensures that basic functions work right, and that methods have documentation.
    (Yes, method docstrings are enforced)

    Author: CraftSpider
"""

import pytest
import string
import spidertools.common.utils as utils

from pathlib import Path


def test_keygen():

    key = utils.key_generator()
    assert len(key) == 6, "Key length doesn't match expected"
    assert key.isalnum(), "Key characters don't match expected"

    key = utils.key_generator(size=10)
    assert len(key) == 10, "Key length parameter doesn't match returned length"
    assert key.isalnum(), "Key characters don't match expected"

    key = utils.key_generator(chars=string.digits)
    assert len(key) == 6, "Key length doesn't match expected"
    assert key.isdecimal(), "Key characters paramter don't match returned key"


def test_replace():

    test_str = "\\n \\t \\s"
    expected = "\n \t  "
    replaced = utils.replace_escapes(test_str)
    assert replaced == expected, "Escapes not replaced"

    test_str = "\\\\n \\\\t \\\\s"
    expected = "\\n \\t \\s"
    replaced = utils.replace_escapes(test_str)
    assert replaced == expected, "Slash escapes not respected"


def test_safe_remove():
    with open("temp.txt", "w") as file:
        pass

    assert Path("temp.txt").exists(), "Failed pre-test file existence check"
    assert not Path("temp.xml").exists(), "Failed pre-test file existence check"

    utils.safe_remove("temp.txt", "temp.xml")

    assert not Path("temp.txt").exists(), "File wasn't deleted"
    assert not Path("temp.xml").exists(), "File somehow appeared???"


def test_case_checkers():

    test = "lower_snake_case"
    assert utils.get_type(test) == "lower snake"
    test = "UPPER_SNAKE_CASE"
    assert utils.get_type(test) == "upper snake"
    test = "lowerCamelCase"
    assert utils.get_type(test) == "lower camel"
    test = "UpperCamelCase"
    assert utils.get_type(test) == "upper camel"
    test = "any other"
    assert utils.get_type(test) == "other"


def test_case_splitters():

    test = "lower_snake_case"
    result = utils.split_snake(test)
    assert result == ("lower", "snake", "case")
    result = utils.split_snake(test, False)
    assert result == ("lower", "snake", "case")

    test = "UPPER_SNAKE_CASE"
    result = utils.split_snake(test)
    assert result == ("upper", "snake", "case")
    result = utils.split_snake(test, False)
    assert result == ("UPPER", "SNAKE", "CASE")

    test = "lowerCamelCase"
    result = utils.split_camel(test)
    assert result == ("lower", "camel", "case")
    result = utils.split_camel(test, False)
    assert result == ("lower", "Camel", "Case")

    test = "UpperCamelCase"
    result = utils.split_camel(test)
    assert result == ("upper", "camel", "case")
    result = utils.split_camel(test, False)
    assert result == ("Upper", "Camel", "Case")

    test = "URLIsAnEdgeCaseIReallyDislike"
    result = utils.split_camel(test, False)
    assert result == ("URL", "Is", "An", "Edge", "Case", "I", "Really", "Dislike")


def test_case_converters():

    test_str = "lower_snake_case"
    expected = "LowerSnakeCase"
    result = utils.to_camel_case(test_str)
    assert result == expected, "Snake case not converted to upper camel case"

    expected = "lowerSnakeCase"
    result = utils.to_camel_case(test_str, False)
    assert result == expected, "Snake case not converted to lower camel case"

    test_str = "UpperCamelCase"
    expected = "upper_camel_case"
    result = utils.to_snake_case(test_str)
    assert result == expected, "Camel case not converted to lower snake case"

    expected = "UPPER_CAMEL_CASE"
    result = utils.to_snake_case(test_str, True)
    assert result == expected, "Camel case not converted to upper snake case"


def test_zero_pad():
    test_str = "1 01 001"

    expected = "1 01 001"
    result = utils.zero_pad(test_str, 1)
    assert result == expected, "Length of one should leave string unchanged"

    expected = "01 01 001"
    result = utils.zero_pad(test_str, 2)
    assert result == expected, "Length of two affects numbers lengths less than two"

    expected = "001 001 001"
    result = utils.zero_pad(test_str, 3)
    assert result == expected, "Length of three pads all numbers to three digits"

    with pytest.raises(ValueError):
        utils.zero_pad("", -1)
        pytest.fail("Negative length failed to raise error")
