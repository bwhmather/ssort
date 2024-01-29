from ssort._builtins import MODULE_BUILTINS
from ssort._graphs import Graph


def module_statements_graph(statements):
    """
    Constructs a graph of the interdependencies in a list of module level
    statements.

    :param statements:
        An ordered list of opaque `Statement` objects from which to construct
        the graph.

    :returns:
        A `Graph` mapping from statements to the set of statements that they
        depend on.
    """
    # A dictionary mapping from names to the statements which bind them.
    scope = {}

    all_requirements = []
    resolved = {}

    for statement in statements:
        for requirement in statement.requirements():
            all_requirements.append(requirement)

            if requirement.name in scope:
                resolved[requirement] = scope[requirement.name]
                continue

            if requirement.name in MODULE_BUILTINS:
                resolved[requirement] = None
                continue

        for name in statement.bindings():
            scope[name] = statement

    # Patch up dependencies that couldn't be resolved immediately.
    for requirement in all_requirements:
        if requirement in resolved:
            continue

        if requirement.name not in scope:
            continue

        resolved[requirement] = scope[requirement.name]

    graph = Graph()
    for statement in statements:
        graph.add_node(statement)

    for statement in statements:
        for requirement in statement.requirements():
            if resolved.get(requirement) is not None:
                graph.add_dependency(statement, resolved[requirement])

    # Add links between statements that overwrite the same binding to make sure
    # that bindings are always applied in the same order.
    scope = {}
    for statement in statements:
        for name in statement.bindings():
            if name in scope:
                graph.add_dependency(statement, scope[name])
            scope[name] = statement

    return graph


def class_statements_initialisation_graph(statements):
    """
    Constructs a graph of the hard dependencies within a list of class level
    statements.  These are dependencies that absolutely cannot be reordered
    without changing the semantics of the script.

    At inititialisation, class level statements can see earlier bindings in the
    class body.

    Note that this isn't a proper scope: variables from the containing scope are
    not shadowed until after a binding is actually made and, obviously from the
    need for a `self` argument, bindings are not captured.

    The following example demonstrates some of this behaviour:

    .. code:: python

        >>> r = 1
        >>> class A:
        ...     a = r
        ...     r = 2
        ...     b = r
        >>> r
        1
        >>> A.a
        1
        >>> A.b
        2

    If a name cannot be resolved at the class level we assume that it is
    resolved at the module level and don't emit any warning.

    :param statements:
        An ordered list of opaque `Statement` objects from which to construct
        the graph.

    :returns:
        A `Graph` mapping from statements to the set of statements that they
        depend on.
    """
    scope = {}

    graph = Graph()

    for statement in statements:
        graph.add_node(statement)

        for requirement in statement.requirements():
            if requirement.deferred:
                continue

            if requirement.name not in scope:
                continue

            graph.add_dependency(statement, scope[requirement.name])

        for name in statement.bindings():
            scope[name] = statement

    return graph


def class_statements_runtime_graph(statements, *, ignore_public):
    """
    Attempts to construct a graph of the soft, runtime dependencies between the
    methods of a class.

    The graph is inferred by looking for attribute access on the `self` argument
    of methods.

    :param statements:
        An ordered list of opaque `Statement` objects from which to construct
        the graph.
    :param ignore_public:
        If true, the graph will only include references to private attributes,
        i.e attributes prefixed by `_`.  This leaves the sorting of public
        methods, which make up the interface of the class, to the programmer.

    :returns:
        A `Graph` mapping from statements to the set of statements that they
        depend on.
    """
    scope = {}

    graph = Graph()

    for statement in statements:
        graph.add_node(statement)

        for name in statement.bindings():
            scope[name] = statement

    for statement in statements:
        for name in statement.method_requirements():
            if ignore_public and not name.startswith("_"):
                continue
            if name not in scope:
                continue
            graph.add_dependency(statement, scope[name])

    return graph
