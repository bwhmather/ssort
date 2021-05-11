import builtins

from ssort._builtins import CLASS_BUILTINS, MODULE_BUILTINS


def test_no_new_module_builtins():
    # Checks that python hasn't introduced any new builtins that aren't in our
    # list.
    assert not set(builtins.__dict__) - MODULE_BUILTINS


def test_no_new_class_builtins():
    class Cls:
        builtins = locals()

    assert not set(Cls.builtins) - {"builtins", *CLASS_BUILTINS}
