import pathlib

import pytest

from ssort import ssort

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


@pytest.mark.parametrize("example", examples)
def test_idempotent(example):
    examples_dir = pathlib.Path("examples")
    input_path = examples_dir / f"{example}_input.py"
    input_text = input_path.read_text()

    sorted_text = ssort(input_text, filename=str(input_path))
    resorted_text = ssort(sorted_text, filename=str(input_path))

    assert resorted_text == sorted_text
