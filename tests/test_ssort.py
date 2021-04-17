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
        def a():
            return b()
        def b():
            return c()
        def c():
            return a()
        """
    )
    expected = _clean(
        """
        def a():
            return b()
        def b():
            return c()
        def c():
            return a()
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_cycle_reversed():
    original = _clean(
        """
        def a():
            return c()
        def b():
            return a()
        def c():
            return b()
        """
    )
    expected = _clean(
        """
        def a():
            return c()
        def b():
            return a()
        def c():
            return b()
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_cycle_with_dependant():
    original = _clean(
        """
        def c():
            return a()
        def a():
            return b()
        def b():
            return a()
        """
    )
    expected = _clean(
        """
        def a():
            return b()
        def c():
            return a()
        def b():
            return a()
        """
    )
    actual = ssort(original)
    assert actual == expected
