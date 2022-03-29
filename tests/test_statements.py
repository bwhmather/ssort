from ssort._parsing import parse


def test_statement_text_padded_same_row():
    statements = list(parse("a = 4; b = 5"))
    assert statements[1].text_padded() == "       b = 5"


def test_statement_text_padded_separate_rows():
    statements = list(parse("a = 4\n\nb = 5"))
    assert statements[1].text_padded() == "\n\nb = 5"
