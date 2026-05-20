"""
The `pretty_print` utils.
It recursively calls itself.
"""

from functools import singledispatch


def get_indent(level: int) -> str:
    """
    Turns an indent level into a string.
    """

    return " " * (4 * level)


@singledispatch
def pretty_print(value, indent_level: int = 0) -> str:
    """
    `pretty_print` function for generic arguments.
    """

    return get_indent(indent_level) + str(value)


@pretty_print.register
def _(value: str, indent_level: int = 0) -> str:
    """
    `pretty_print` function for 'string' arguments.
    """

    return get_indent(indent_level) + repr(value)


@pretty_print.register
def _(d: dict, indent_level: int = 0) -> str:
    """
    `pretty_print` function for 'dictionnaries' arguments.
    """

    if len(d) == 0:
        return get_indent(indent_level) + "{}"

    lines = [get_indent(indent_level) + '{']

    for i, (k, v) in enumerate(d.items()):
        line = (
            get_indent(indent_level + 1)
            + repr(k) + ": "
            + pretty_print(v, indent_level + 1).lstrip()
        )

        if i != len(d) - 1:
            line += ','

        lines.append(line)

    lines.append(get_indent(indent_level) + '}')
    return "\n".join(lines)


@pretty_print.register
def _(lst: list, indent_level: int = 0) -> str:
    """
    `pretty_print` function for 'list' arguments.
    """

    if lst == []:
        return get_indent(indent_level) + "[]"

    lines = [get_indent(indent_level) + '[']

    for i, element in enumerate(lst):
        line = pretty_print(element, indent_level + 1)

        if i != len(lst) - 1:
            line += ','

        lines.append(line)

    lines.append(get_indent(indent_level) + ']')
    return "\n".join(lines)
