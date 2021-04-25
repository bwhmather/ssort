import ast
from io import StringIO
from token import NAME
from tokenize import generate_tokens

from ssort._statements import (
    Statement,
    statement_node,
    statement_text,
    statement_text_padded,
)


def _find_start(node):
    if (
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and node.decorator_list
    ):
        decorator = node.decorator_list[0]
        return decorator.lineno - 1, decorator.col_offset
    else:
        return node.lineno - 1, node.col_offset


def _find_end(node):
    return node.end_lineno - 1, node.end_col_offset


def split(
    root_text,
    *,
    nodes=None,
    next_row=0,
    next_col=0,
    indent=0,
    filename="<unknown>"
):
    # Build an index of row lengths and start offsets to enable fast string
    # indexing using ast row/column coordinates.
    row_lengths = []
    row_offsets = [0]
    for offset, char in enumerate(root_text):
        if char == "\n":
            row_lengths.append(offset - row_offsets[-1])
            row_offsets.append(offset + 1)
    row_lengths.append(len(root_text) - row_offsets[-1])

    if nodes is None:
        root_node = ast.parse(root_text, filename)
        nodes = iter(root_node.body)
    else:
        nodes = iter(nodes)

    next_node = next(nodes, None)

    if next_node is not None:
        next_start_row, next_start_col = _find_start(next_node)
        next_end_row, next_end_col = _find_end(next_node)

        indent_text = " " * next_node.col_offset
        next_indent_text = ""

    while next_node:
        this_node, next_node = next_node, next(nodes, None)
        this_end_row, this_end_col = next_end_row, next_end_col
        this_indent_text = next_indent_text

        if next_node is not None:
            next_start_row, next_start_col = _find_start(next_node)
            next_end_row, next_end_col = _find_end(next_node)

        start_row = next_row
        start_col = next_col

        if next_node is not None and this_end_row == next_end_row:
            # There is another statement on the same line.  It should be
            # possible to claim as far as the start of the next node for this
            # node, but this space can only contain semicolons and whitespace
            # so we are better off filtering it out.
            end_row = this_end_row
            end_col = this_end_col

            next_row = next_start_row
            next_col = next_start_col

            next_indent_text = indent_text
        else:
            # No other statements on the same line.  Assume that everything up
            # until the end of the line is comments attached to this statement.
            end_row = this_end_row
            end_col = row_lengths[end_row]

            next_row = this_end_row + 1
            next_col = 0

            next_indent_text = ""

        start_offset = row_offsets[start_row] + start_col
        end_offset = row_offsets[end_row] + end_col

        yield Statement(
            text=this_indent_text + root_text[start_offset:end_offset],
            node=this_node,
            start_row=start_row,
            start_col=start_col,
        )


def split_class(statement):
    node = statement_node(statement)
    text = statement_text(statement)
    text_padded = statement_text_padded(statement)

    # Build an index of row lengths and start offsets to enable fast string
    # indexing using ast row/column coordinates.
    row_lengths = []
    row_offsets = [0]
    for offset, char in enumerate(text_padded):
        if char == "\n":
            row_lengths.append(offset - row_offsets[-1])
            row_offsets.append(offset + 1)
    row_lengths.append(len(text_padded) - row_offsets[-1])

    tokens = iter(generate_tokens(StringIO(text_padded).readline))

    for token in tokens:
        lineno, col_offset = token.start
        if lineno == node.lineno and col_offset == node.col_offset:
            assert token.string == "class"
            break

    token = next(tokens)
    assert token.type == NAME

    token = next(tokens)
    if token.string == "(":
        token = next(tokens)
        depth = 1
        while depth:
            if token.string == "(":
                depth += 1
            if token.string == ")":
                depth -= 1
            token = next(tokens)

    assert token.string == ":"

    if node.body[0].lineno == token.end[0]:
        # All tokens are on the same line.  `split` won't know how to indent
        # them so we do it ourselves.
        head_end_lineno, head_end_col = token.end
        head_end_row = head_end_lineno - 1

        head_end_offset = row_offsets[head_end_row] + head_end_col
        head_text_padded = text_padded[:head_end_offset].rstrip()
        head_text = head_text_padded[len(text_padded) - len(text) :]

        body_statements = []
        for child_node in node.body:
            child_start_row, child_start_col = _find_start(child_node)
            child_end_row, child_end_col = _find_end(child_node)

            assert child_start_row == head_end_row
            assert child_end_row == head_end_row

            start_offset = row_offsets[child_start_row] + child_start_col
            end_offset = row_offsets[child_end_row] + child_end_col

            body_statements.append(
                Statement(
                    text="    " + text_padded[start_offset:end_offset],
                    node=child_node,
                    start_row=child_start_row,
                    start_col=child_start_col,
                )
            )

    else:
        head_end_lineno, head_end_col = token.end[0] + 1, 0
        head_end_row = head_end_lineno - 1

        head_end_offset = row_offsets[head_end_row] + head_end_col
        head_text_padded = text_padded[:head_end_offset].rstrip()
        head_text = head_text_padded[len(text_padded) - len(text) :]

        body_text_padded = (
            (head_end_row) * "\n"
            + head_end_col * " "
            + text_padded[head_end_offset:]
        )

        body_statements = list(
            split(
                body_text_padded,
                nodes=node.body,
                next_row=head_end_row,
                next_col=head_end_col,
            )
        )

    return head_text, body_statements
