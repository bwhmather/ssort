from ssort._parsing import split
from ssort._statements import statement_text_padded


def test_statement_text_padded_same_row():
    statements = list(split("a = 4; b = 5"))
    assert statement_text_padded(statements[1]) == "       b = 5"


def test_statement_text_padded_separate_rows():
    statements = list(split("a = 4\n\nb = 5"))
    assert statement_text_padded(statements[1]) == "\n\nb = 5"
