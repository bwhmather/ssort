import pathlib

import pytest

from ssort import ssort
from ssort._dependencies import statement_dependencies
from ssort._graphs import Graph, replace_cycles, topological_sort
from ssort._modules import Module, statement_text
from ssort._presort import presort
from ssort._utils import sort_key_from_iter

examples = [
    "distlib_compat",
    "dnspython_versioned",
    "isort_finders",
    "pillow_BdfFontFile",
    "pillow_Image",
    "setuptools_bdist",
    "setuptools_init",
    "setuptools_msvccompiler",
    "sqlalchemy_base",
]


@pytest.mark.parametrize("example", examples)
def test_examples(example):
    examples_dir = pathlib.Path("examples")
    input_path = examples_dir / f"{example}_input.py"
    output_path = examples_dir / f"{example}_output.py"
    input_text = input_path.read_text()

    actual_text = ssort(input_text, filename=str(input_path))

    # XXX Uncomment to update samples. XXX
    # output_path.write_text(actual_text)
    # XXX Don't forget to restore re-comment after. XXX

    expected_text = output_path.read_text()

    assert actual_text == expected_text


def _presort(input_text, *, filename):
    module = Module(input_text, filename=filename)
    presorted = presort(module)
    return "\n".join(statement_text(module, stmt) for stmt in presorted) + "\n"


@pytest.mark.parametrize("example", examples)
def test_presort_is_stable(example):
    examples_dir = pathlib.Path("examples")
    input_path = examples_dir / f"{example}_input.py"
    input_text = input_path.read_text()

    a = _presort(input_text, filename=str(input_path))
    b = _presort(input_text, filename=str(input_path))

    assert a == b


@pytest.mark.parametrize("example", examples)
def test_presort_sort_is_idempotent(example):
    examples_dir = pathlib.Path("examples")
    input_path = examples_dir / f"{example}_input.py"
    input_text = input_path.read_text()

    a = _presort(input_text, filename=str(input_path))
    b = _presort(a, filename=str(input_path))

    assert a == b


def _topological_sort(input_text, *, filename):
    module = Module(input_text, filename=filename)
    graph = Graph.from_dependencies(
        module.statements(),
        lambda statement: statement_dependencies(module, statement),
    )
    replace_cycles(graph, key=sort_key_from_iter(module.statements()))
    toposorted = topological_sort(graph)
    return (
        "\n".join(statement_text(module, stmt) for stmt in toposorted) + "\n"
    )


@pytest.mark.parametrize("example", examples)
def test_topological_sort_is_stable(example):
    examples_dir = pathlib.Path("examples")
    input_path = examples_dir / f"{example}_input.py"
    input_text = input_path.read_text()

    a = _topological_sort(input_text, filename=str(input_path))
    b = _topological_sort(input_text, filename=str(input_path))

    assert a == b


@pytest.mark.parametrize("example", examples)
def test_topological_sort_is_idempotent(example):
    examples_dir = pathlib.Path("examples")
    input_path = examples_dir / f"{example}_input.py"
    input_text = input_path.read_text()

    a = _topological_sort(input_text, filename=str(input_path))
    b = _topological_sort(a, filename=str(input_path))

    assert a == b
