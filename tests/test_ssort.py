import sys
import textwrap

import pytest

from ssort import ssort

type_parameter_syntax = pytest.mark.skipif(
    sys.version_info < (3, 12),
    reason="type parameter syntax was introduced in python 3.12",
)


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
            column = None
            __tablename__ = "table"
            other_column = None
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_mixed_runtime_initialisation():
    original = _clean(
        """
        class Loopy:

            def method(self):
                return self._method()

            attr = method

            def _method(self):
                pass
        """
    )

    expected = _clean(
        """
        class Loopy:

            def _method(self):
                pass

            def method(self):
                return self._method()

            attr = method
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_walrus():
    original = _clean(
        """
        def fun():
            if (a := nofun()):
                return a
            else:
                return True
        def nofun():
            return False
        """
    )
    expected = _clean(
        """
        def nofun():
            return False
        def fun():
            if (a := nofun()):
                return a
            else:
                return True
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_attribute_assign_class_example():
    original = _clean(
        """
        import admin
        class TestAdmin(admin.ModelAdmin):
            list_filter = ("foo_method",)
            def foo_method(self, obj):
                return "something"
            foo_method.short_description = "Foo method"
        """
    )
    expected = _clean(
        """
        import admin
        class TestAdmin(admin.ModelAdmin):
            list_filter = ("foo_method",)
            def foo_method(self, obj):
                return "something"
            foo_method.short_description = "Foo method"
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_iter_unpack_in_class():
    original = _clean(
        """
        class MyClass:
            def method(self):
                a, *b = 1, 2, 3
        """
    )
    expected = _clean(
        """
        class MyClass:
            def method(self):
                a, *b = 1, 2, 3
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_overload_decorator():
    original = _clean(
        """
        from typing import overload
        def g():
            f(1)
        @overload
        def f(x: int) -> int:
            ...
        @overload
        def f(x: str) -> str:
            ...
        def f(x: int | str) -> int | str:
            print(x)
            return x
        if __name__ == "__main__":
            f(5)
        """
    )
    expected = _clean(
        """
        from typing import overload
        @overload
        def f(x: int) -> int:
            ...
        @overload
        def f(x: str) -> str:
            ...
        def f(x: int | str) -> int | str:
            print(x)
            return x
        def g():
            f(1)
        if __name__ == "__main__":
            f(5)
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_concat():
    original = _clean(
        """
        def f():
            return l
        l = []
        l += 1
        """
    )
    expected = _clean(
        """
        l = []
        l += 1
        def f():
            return l
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_inner_class():
    original = _clean(
        """
        class Outer:
            '''
            The outer class.
            '''
            a = 4
            class Inner:
                pass
            __slots__ = ("b",)
        """
    )
    expected = _clean(
        """
        class Outer:
            '''
            The outer class.
            '''
            __slots__ = ("b",)
            class Inner:
                pass
            a = 4
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_lifecycle_class():
    original = _clean(
        """
        class Thing:
            def startup(self):
                ...
            def poll(self):
                try:
                    ...
                except:
                    self.shutdown()
            def shutdown(self):
                ...
        """
    )
    expected = _clean(
        """
        class Thing:
            def startup(self):
                ...
            def poll(self):
                try:
                    ...
                except:
                    self.shutdown()
            def shutdown(self):
                ...
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_lifecycle_class_private():
    original = _clean(
        """
        class Thing:
            def startup(self):
                ...
            def poll(self):
                try:
                    ...
                except:
                    self._shutdown_inner()
            def _shutdown_inner(self):
                ...
            def shutdown(self):
                self._shutdown_inner
        """
    )
    expected = _clean(
        """
        class Thing:
            def startup(self):
                ...
            def _shutdown_inner(self):
                ...
            def poll(self):
                try:
                    ...
                except:
                    self._shutdown_inner()
            def shutdown(self):
                self._shutdown_inner
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_single_comment():
    original = _clean(
        """
        # This is a file with just a single comment!
        """
    )
    expected = _clean(
        """
        # This is a file with just a single comment!
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_ssort_preserve_crlf_endlines_bytes():
    original = b"a = b\r\nb = 4"
    expected = b"b = 4\r\na = b\r\n"

    actual = ssort(original)
    assert actual == expected


def test_ssort_preserve_crlf_endlines_str():
    original = "a = b\r\nb = 4"
    expected = "b = 4\r\na = b\r\n"

    actual = ssort(original)
    assert actual == expected


def test_ssort_list_comp_conflicts_with_global_scope():
    original = _clean(
        """
        def f():
            g()
            return [g for g in range(10)]
        def g():
            pass
        """
    )
    expected = _clean(
        """
        def g():
            pass
        def f():
            g()
            return [g for g in range(10)]
        """
    )

    actual = ssort(original)
    assert actual == expected


def test_ssort_set_comp_conflicts_with_global_scope():
    original = _clean(
        """
        def f():
            g()
            return {g for g in range(10)}
        def g():
            pass
        """
    )
    expected = _clean(
        """
        def g():
            pass
        def f():
            g()
            return {g for g in range(10)}
        """
    )

    actual = ssort(original)
    assert actual == expected


def test_ssort_dict_comp_conflicts_with_global_scope():
    original = _clean(
        """
        def f():
            g()
            return {g: 1 for g in range(10)}
        def g():
            pass
        """
    )
    expected = _clean(
        """
        def g():
            pass
        def f():
            g()
            return {g: 1 for g in range(10)}
        """
    )

    actual = ssort(original)
    assert actual == expected


def test_ssort_generator_exp_conflicts_with_global_scope():
    original = _clean(
        """
        def f():
            g()
            return (g for g in range(10))
        def g():
            pass
        """
    )
    expected = _clean(
        """
        def g():
            pass
        def f():
            g()
            return (g for g in range(10))
        """
    )

    actual = ssort(original)
    assert actual == expected


def test_ssort_self_positional_only():
    original = _clean(
        """
        class C:
            def fun(self, arg, /, notself):
                return notself._notdep()

            def _notdep(self):
                pass
        """
    )
    expected = _clean(
        """
        class C:
            def fun(self, arg, /, notself):
                return notself._notdep()

            def _notdep(self):
                pass
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_single_line_dummy_function():
    original = "def fun(): ...\n"
    expected = "def fun(): ...\n"

    actual = ssort(original)
    assert actual == expected


def test_single_line_dummy_class():
    original = "class Class: ...\n"
    expected = "class Class: ...\n"

    actual = ssort(original)
    assert actual == expected


@type_parameter_syntax
def test_ssort_type_alias():
    original = _clean(
        """
        from decimal import Decimal

        roundint(3.14)

        def roundint(n: N) -> int:
            return int(round(n))

        type N = Decimal | float
        """
    )
    expected = _clean(
        """
        from decimal import Decimal

        type N = Decimal | float

        def roundint(n: N) -> int:
            return int(round(n))

        roundint(3.14)
        """
    )
    actual = ssort(original)
    assert actual == expected


@type_parameter_syntax
def test_ssort_generic_function():
    original = _clean(
        """
        func(4)
        def func[T](a: T) -> T:
            return a
        """
    )
    expected = _clean(
        """
        def func[T](a: T) -> T:
            return a
        func(4)
        """
    )
    actual = ssort(original)
    assert actual == expected


@type_parameter_syntax
def test_ssort_generic_class():
    original = _clean(
        """
        obj = ClassA[str]()
        class ClassA[T: (str, bytes)](BaseClass[T]):
            attr1: T
        class BaseClass[T]:
            pass
        """
    )
    expected = _clean(
        """
        class BaseClass[T]:
            pass
        class ClassA[T: (str, bytes)](BaseClass[T]):
            attr1: T
        obj = ClassA[str]()
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_overload_variants():
    original = _clean(
        """
        from typing import overload

        def _get_value() -> int:
            return 0

        @overload
        def func(self, first: int, second: int) -> int: ...
        def func(self, both: tuple[int, int]) -> int:
            return _get_value()
        """
    )
    expected = _clean(
        """
        from typing import overload

        def _get_value() -> int:
            return 0

        @overload
        def func(self, first: int, second: int) -> int: ...
        def func(self, both: tuple[int, int]) -> int:
            return _get_value()
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_method_overload_variants():
    original = _clean(
        """
        from typing import Any, Generic, TypeVar, overload

        T = TypeVar("T")

        class MyClass(Generic[T]):
            def _get_value(self):
                return 0

            @overload
            def __get__(self, instance: None, owner=None) ->  MyClass(Generic[T]): ...
            @overload
            def __get__(self, instance: Any, owner=None) -> T: ...
            def __get__(self, instance, owner=None):
                if instance is None:
                    return self
                return self._get_value()
        """
    )
    expected = _clean(
        """
        from typing import Any, Generic, TypeVar, overload

        T = TypeVar("T")

        class MyClass(Generic[T]):
            def _get_value(self):
                return 0

            @overload
            def __get__(self, instance: None, owner=None) ->  MyClass(Generic[T]): ...
            @overload
            def __get__(self, instance: Any, owner=None) -> T: ...
            def __get__(self, instance, owner=None):
                if instance is None:
                    return self
                return self._get_value()
        """
    )
    actual = ssort(original)
    assert actual == expected


def test_method_overload_variants_qualified():
    original = _clean(
        """
        from typing import Any, Generic, TypeVar
        import typing

        T = TypeVar("T")

        class MyClass(Generic[T]):
            def _get_value(self):
                return 0

            @typing.overload
            def __get__(self, instance: None, owner=None) -> MyClass(Generic[T]): ...
            @typing.overload
            def __get__(self, instance: Any, owner=None) -> T: ...
            def __get__(self, instance, owner=None):
                if instance is None:
                    return self
                return self._get_value()
        """
    )
    expected = _clean(
        """
        from typing import Any, Generic, TypeVar
        import typing

        T = TypeVar("T")

        class MyClass(Generic[T]):
            def _get_value(self):
                return 0

            @typing.overload
            def __get__(self, instance: None, owner=None) -> MyClass(Generic[T]): ...
            @typing.overload
            def __get__(self, instance: Any, owner=None) -> T: ...
            def __get__(self, instance, owner=None):
                if instance is None:
                    return self
                return self._get_value()
        """
    )
    actual = ssort(original)
    assert actual == expected
