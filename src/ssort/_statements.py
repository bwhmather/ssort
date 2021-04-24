from ssort._bindings import get_bindings
from ssort._method_requirements import get_method_requirements
from ssort._requirements import get_requirements


class Statement:
    def __init__(self, *, text, node, start_row, start_col):
        self._text = text
        self._node = node
        self._start_row = start_row
        self._start_col = start_col

    def __repr__(self):
        return f"<Statement text={self._text!r}>"


def statement_node(statement):
    return statement._node


def statement_text(statement):
    return statement._text


def statement_text_padded(statement):
    """
    Return the statement text padded with leading whitespace so that
    coordinates in the ast match up with coordinates in the text.
    """
    return (
        ("\n" * statement._start_row)
        + (" " * statement._start_col)
        + statement._text
    )


def statement_requirements(statement):
    """
    Returns an iterable yielding Requirement objects describing the bindings
    that a statement references.
    """
    return get_requirements(statement_node(statement))


def statement_method_requirements(statement):
    """
    Returns an iterable yielding the names of attributes of the `self` parameter
    that a statement depends on.
    """
    return get_method_requirements(statement_node(statement))


def statement_bindings(statement):
    """
    Returns an iterable yielding the names bound by a statement.
    """
    return get_bindings(statement_node(statement))
