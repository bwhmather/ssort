import ast


def _find_start(node):
    lineno, col = min(
        (descendant.lineno, descendant.col_offset)
        for descendant in ast.walk(node)
        if hasattr(descendant, "lineno") and hasattr(descendant, "col_offset")
    )
    return lineno - 1, col


def _find_end(node):
    lineno, col = max(
        (descendant.end_lineno, descendant.end_col_offset)
        for descendant in ast.walk(node)
        if hasattr(descendant, "end_lineno")
        and hasattr(descendant, "end_col_offset")
    )
    return lineno - 1, col


def split(root_text, *, filename="<unknown>"):
    root_node = ast.parse(root_text, filename)

    # Build an index of row lengths and start offsets to enable fast string
    # indexing using ast row/column coordinates.
    row_lengths = []
    row_offsets = [0]
    for offset, char in enumerate(root_text):
        if char == "\n":
            row_lengths.append(offset - row_offsets[-1])
            row_offsets.append(offset + 1)
    row_lengths.append(len(root_text) - row_offsets[-1])

    nodes = iter(root_node.body)

    next_row = 0
    next_col = 0

    next_node = next(nodes, None)

    if next_node is not None:
        next_start_row, next_start_col = _find_start(next_node)
        next_end_row, next_end_col = _find_end(next_node)

    while next_node:
        this_node, next_node = next_node, next(nodes, None)
        this_end_row, this_end_col = next_end_row, next_end_col

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
        else:
            # No other statements on the same line.  Assume that everything up
            # until the end of the line is comments attached to this statement.
            end_row = this_end_row
            end_col = row_lengths[end_row]

            next_row = this_end_row + 1
            next_col = 0

        start_offset = row_offsets[start_row] + start_col
        end_offset = row_offsets[end_row] + end_col

        yield root_text[start_offset:end_offset], this_node
