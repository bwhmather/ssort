import ast


def split(f, filename):
    root_text = f.read()
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
    while True:
        this_node, next_node = next_node, next(nodes, None)
        if this_node is None:
            break

        start_row = next_row
        start_col = next_col

        if next_node is not None and this_node.end_lineno == next_node.lineno:
            # There is another statement on the same line.  It should be
            # possible to claim as far as the start of the next node for this
            # node, but this space can only contain semicolons and whitespace
            # so we are better off filtering it out.
            end_row = this_node.end_lineno - 1
            end_col = this_node.end_col_offset

            next_row = next_node.lineno - 1
            next_col = next_node.col_offset
        else:
            # No other statements on the same line.  Assume that everything up
            # until the end of the line is comments attached to this statement.
            end_row = this_node.lineno - 1
            end_col = row_lengths[end_row]

            next_row = this_node.lineno
            next_col = 0

        start_offset = row_offsets[start_row] + start_col
        end_offset = row_offsets[end_row] + end_col

        yield root_text[start_offset:end_offset], this_node
