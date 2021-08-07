import textwrap

from ssort import ssort


def _clean(text):
    return textwrap.dedent(text).strip() + "\n"


def test_empty():
    original = ""
    expected = ""
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


def test_depencency_order():
    # TODO We previously tried to reorder dependencies to match the order they
    # were required in.
    original = _clean(
        """
        def _step2():
            ...
        def _step1():
            ...
        def main():
            _step1()
            _step2()
        """
    )
    expected = _clean(
        """
        def _step2():
            ...
        def _step1():
            ...
        def main():
            _step1()
            _step2()
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_isort_finders():
    original = _clean(
        """
        class Base:
            pass

        def a():
            pass

        class A(Base):
            def method():
                a()

        class B(Base):
            pass

        def something():
            return [A, B]
        """
    )
    expected = _clean(
        """
        class Base:
            pass

        def a():
            pass

        class A(Base):
            def method():
                a()

        class B(Base):
            pass

        def something():
            return [A, B]
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_single_dispatch():
    original = _clean(
        """
        import functools

        @functools.singledispatch
        def fun(x):
            ...

        @fun.register(str)
        def _fun_str(x):
            ...

        @fun.register(int)
        def _fun_int(x):
            ...

        if __name__ == "__main__":
            fun()
        """
    )
    expected = _clean(
        """
        import functools

        @functools.singledispatch
        def fun(x):
            ...

        @fun.register(str)
        def _fun_str(x):
            ...

        @fun.register(int)
        def _fun_int(x):
            ...

        if __name__ == "__main__":
            fun()
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_slots():
    original = _clean(
        """
        class Struct:
            int_attr: int
            __slots__ = ("int_attr", "str_attr")
            str_attr: str
        """
    )
    expected = _clean(
        """
        class Struct:
            __slots__ = ("int_attr", "str_attr")
            int_attr: int
            str_attr: str
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_pretend_dunder_properties():
    original = _clean(
        """
        class Table:
            column = None
            __tablename__ = "table"
            __slots__ = ("column", "other_column")
            other_column = None
        """
    )
    expected = _clean(
        """
        class Table:
            __slots__ = ("column", "other_column")
            __tablename__ = "table"
            column = None
            other_column = None
        """
    )
    actual = ssort(original)
    assert actual == expected
