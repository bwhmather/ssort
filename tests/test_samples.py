import pathlib

from ssort import ssort


def pytest_generate_tests(metafunc):
    examples_dir = pathlib.Path("test_data/samples")

    examples = []
    for input_path in examples_dir.glob("*_input.py"):
        examples.append(input_path.name[: -len("_input.py")])
    examples.sort()
    assert examples

    metafunc.parametrize("example", examples)


def test_examples(example):
    examples_dir = pathlib.Path("test_data/samples")
    input_path = examples_dir / f"{example}_input.py"
    output_path = examples_dir / f"{example}_output.py"
    input_text = input_path.read_text()

    actual_text = ssort(
        input_text,
        filename=str(input_path),
        on_wildcard_import=lambda **kwargs: None,
    )

    # XXX Uncomment to update samples. XXX
    # output_path.write_text(actual_text)
    # XXX Don't forget to restore re-comment after. XXX

    expected_text = output_path.read_text()

    assert actual_text == expected_text


def test_idempotent(example):
    examples_dir = pathlib.Path("test_data/samples")
    input_path = examples_dir / f"{example}_input.py"
    input_text = input_path.read_text()

    sorted_text = ssort(
        input_text,
        filename=str(input_path),
        on_wildcard_import=lambda **kwargs: None,
    )
    resorted_text = ssort(
        sorted_text,
        filename=str(input_path),
        on_wildcard_import=lambda **kwargs: None,
    )

    assert resorted_text == sorted_text
