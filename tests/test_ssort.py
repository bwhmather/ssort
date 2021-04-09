import textwrap

from ssort import ssort


def _clean(text):
    return textwrap.dedent(text).strip() + "\n"


def test_empty():
    original = ""
    expected = "\n"
    actual = ssort(original)
    assert actual == expected


def test_no_trailing_newline():
    original = "a = 1"
    expected = "a = 1\n"
    actual = ssort(original)
    assert actual == expected


def test_trailing_newline():
    original = "b = 2\n"
    expected = "b = 2\n"
    actual = ssort(original)
    assert actual == expected


def test_cycle():
    original = _clean(
        """
        a = b
        b = c
        c = a
        """
    )
    expected = _clean(
        """
        a = b
        b = c
        c = a
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_cycle_reversed():
    original = _clean(
        """
        a = c
        b = a
        c = b
        """
    )
    expected = _clean(
        """
        a = c
        b = a
        c = b
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_cycle_with_dependant():
    original = _clean(
        """
        c = a
        a = b
        b = a
        """
    )
    expected = _clean(
        """
        a = b
        c = a
        b = a
        """
    )
    actual = ssort(original)
    assert actual == expected
