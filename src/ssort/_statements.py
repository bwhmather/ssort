from ssort._bindings import get_bindings
from ssort._requirements import get_requirements


class Statement:
    def __init__(self, *, text, node):
        self._text = text
        self._node = node

    def __repr__(self):
        return f"<Statement text={self._text!r}>"


def statement_node(statement):
    return statement._node


def statement_text(statement):
    return statement._text


def statement_requirements(statement):
    """
    Returns an iterable yielding Requirement objects describing the bindings
    that a statement references.
    """
    return get_requirements(statement_node(statement))


def statement_bindings(statement):
    """
    Returns an iterable yielding the names bound by a statement.
    """
    return get_bindings(statement_node(statement))
