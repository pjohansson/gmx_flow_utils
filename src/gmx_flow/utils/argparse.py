"""Utilities for working with `ArgumentParser` parsers."""

from typing import Optional, TypeVar

T = TypeVar('T')

def parse_type_or_none(value: str, as_type: T) -> Optional[T]:
    """Return a parsed value or `None` if the input is the string 'none'."""

    if value.lower() == 'none':
        return None
    else:
        return as_type(value)


def parse_float_or_none(value: str) -> Optional[float]:
    """Return a parsed float or `None` if the input is the string 'none'."""

    return parse_type_or_none(value, float)
