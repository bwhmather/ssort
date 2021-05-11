import builtins

from ssort._builtins import MODULE_BUILTINS


def test_no_new_module_builtins():
    # Checks that python hasn't introduced any new builtins that aren't in our
    # list.
    assert not set(builtins.__dict__) - MODULE_BUILTINS
