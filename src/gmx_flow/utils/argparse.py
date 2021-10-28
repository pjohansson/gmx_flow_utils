"""Utilities for working with `ArgumentParser` parsers."""


def parse_type_or_none(value, as_type):
    """Return a parsed value or `None` if the input is the string 'none'."""

    if value.lower() == 'none':
        return None 
    else:
        return as_type(value)


def parse_float_or_none(value):
    """Return a parsed float or `None` if the input is the string 'none'."""

    return parse_type_or_none(value, float)
