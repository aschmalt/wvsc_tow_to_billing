import pytest
from tow_conversion.name import Name


def test_name_last_first_format() -> None:
    name = Name("Doe, John")
    assert name.last == "Doe"
    assert name.first == "John"
    assert str(name) == "Doe, John"


def test_name_space_format() -> None:
    name = Name("John Doe")
    assert name.first == "John"
    assert name.last == "Doe"
    assert str(name) == "Doe, John"


def test_name_single_word() -> None:
    name = Name("Cher")
    assert name.first == ""
    assert name.last == ""
    assert str(name) == "Cher"


def test_name_extra_spaces() -> None:
    name = Name("  Doe  ,   John   ")
    assert name.last == "Doe"
    assert name.first == "John"
    assert str(name) == "Doe, John"


def test_name_invalid_comma_format_raises() -> None:
    with pytest.raises(ValueError):
        Name("Doe,John,Smith")


def test_name_with_middle_name() -> None:
    name = Name("John Michael Doe")
    assert name.first == "John Michael"
    assert name.last == "Doe"
    assert str(name) == "Doe, John Michael"


def test_name_with_empty_string() -> None:
    name = Name("")
    assert name.first == ""
    assert name.last == ""
    assert str(name) == ""


def test_name_with_comma_but_no_space() -> None:
    name = Name("Doe,John")
    assert name.last == "Doe"
    assert name.first == "John"
    assert str(name) == "Doe, John"


def test_name_equality_and_hash() -> None:
    name1 = Name("Doe, John")
    name2 = Name("John Doe")
    name3 = Name("Jane Doe")
    name4 = Name("Cher")
    name5 = Name("Cher")
    assert name1 == name2
    assert hash(name1) == hash(name2)
    assert name1 != name3
    assert hash(name1) != hash(name3)
    assert name4 == name5
    assert hash(name4) == hash(name5)
    assert name1 == 'Doe, John'
    assert name1 == 'John Doe'
    assert (name1).__eq__(123) is NotImplemented


def test_name_sorting() -> None:
    names = [
        Name("Jane Doe"),
        Name("Zoe"),
        Name("John Smith"),
        Name("Doe, John"),
        Name("Cher"),
        Name("Smith, Adam"),
    ]
    sorted_names = sorted(names)
    # Cher has empty last/first, so comes first
    assert [str(n) for n in sorted_names] == [
        "Cher",
        "Doe, Jane",
        "Doe, John",
        "Smith, Adam",
        "Smith, John",
        "Zoe"
    ]
    assert Name('Cher') < 'Doe, John'


def test_name_lt_with_non_name() -> None:
    name = Name("Doe, John")
    assert (name).__lt__(123) is NotImplemented
