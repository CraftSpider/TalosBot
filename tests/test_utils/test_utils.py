"""
    Tests Talos utils. Ensures that basic functions work right, and that methods have documentation.
    (Yes, method docstrings are enforced)

    Author: CraftSpider
"""

import pytest
import utils
import string

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
    assert result == expected, "Camel case not converted to snake case"


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

    with pytest.raises(ValueError, message="Negative length failed to raise error"):
        utils.zero_pad("", -1)
