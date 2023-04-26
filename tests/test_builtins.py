import ast
import builtins
import os.path
import subprocess

from ssort._builtins import CLASS_BUILTINS, MODULE_BUILTINS


def _get_builtins():
    return set(dir(builtins))


def _get_class_builtins():
    class Cls:
        builtins = locals()

    return set(Cls.builtins)


def _get_init_builtins():
    import _builtins

    return set(dir(_builtins))


def _get_main_builtins():
    return set(
        ast.literal_eval(
            subprocess.run(
                ["python3", "_builtins"],
                capture_output=True,
                check=True,
                cwd=os.path.dirname(__file__),
                encoding="utf-8",
            ).stdout
        )
    )


def _get_module_builtins():
    from _builtins import module

    return set(dir(module))


def test_no_new_builtins():
    # Checks that python hasn't introduced any new builtins that aren't in our
    # list.
    missing = _get_builtins() - MODULE_BUILTINS
    assert not missing


def test_no_new_class_builtins():
    missing = _get_class_builtins() - {"builtins", *CLASS_BUILTINS}
    assert not missing


def test_no_new_init_builtins():
    missing = _get_init_builtins() - MODULE_BUILTINS
    assert not missing


def test_no_new_main_builtins():
    missing = _get_main_builtins() - MODULE_BUILTINS
    assert not missing


def test_no_new_module_builtins():
    missing = _get_module_builtins() - MODULE_BUILTINS
    assert not missing
