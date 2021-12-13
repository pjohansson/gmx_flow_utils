"""Utilities for working with `ArgumentParser` parsers."""

from argparse import ArgumentParser, _ArgumentGroup, Namespace
from typing import Optional, TypeVar, Iterable, Dict, Any

# From what I understand this is the only way to declare a generic `type` variable
# to use for the type hinting
T = TypeVar('T')


def parse_float_or_none(value: str) -> Optional[float]:
    """Return a parsed float or `None` if the input is the string 'none'."""

    return _parse_type_or_none(value, float)


def _parse_type_or_none(value: str, as_type: T) -> Optional[T]:
    """Return a parsed value or `None` if the input is the string 'none'."""

    if value.lower() == 'none':
        return None
    else:
        return as_type(value)


def add_common_range_args(parser: ArgumentParser,
                          begin: int = 1,
                          end: Optional[int] = None,
                          ext: str = 'dat',
                          ) -> _ArgumentGroup:
    """Add common keyword arguments for file range specification.

    The created argument group is returned.

    """

    parser_range = parser.add_argument_group('range options')

    parser_range.add_argument('-b', '--begin',
                              type=int, default=begin, metavar='INT',
                              help='index of first file to read (default: %(default)s)')
    parser_range.add_argument('-e', '--end',
                              type=int, default=end, metavar='INT',
                              help='index of last file to read (default: %(default)s)')
    parser_range.add_argument('--ext',
                              type=str, default=ext,
                              help='extension for files (default: %(default)s)')

    return parser_range


def add_common_graph_args(parser: ArgumentParser,
                          title: str = '',
                          xlabel: str = r'$x$',
                          ylabel: str = r'$y$',
                          save: Optional[str] = None,
                          dpi: Optional[int] = None,
                          ) -> _ArgumentGroup:
    """Add common keyword arguments for graph specification.

    The created argument group is returned.

    """

    parser_graph = parser.add_argument_group('graph options')

    parser_graph.add_argument('--title',
                              type=str, default=title,
                              help="graph title")
    parser_graph.add_argument('--xlabel',
                              type=str, default=xlabel,
                              help="x axis label")
    parser_graph.add_argument('--ylabel',
                              type=str, default=ylabel,
                              help="y axis label")
    parser_graph.add_argument('--save',
                              type=str, default=save, metavar='PATH',
                              help="save figure to path")
    parser_graph.add_argument('--dpi',
                              type=int, default=dpi,
                              help="dpi of figure")
    parser_graph.add_argument('--transparent',
                              action='store_true',
                              help="save figure with transparent background")
    parser_graph.add_argument('--noshow',
                              action='store_false', dest='show',
                              help="do not show figure window")

    return parser_graph


def get_common_range_kwargs(args: Namespace,
                            keys: Iterable[str] = ['begin', 'end', 'ext'],
                            ) -> Dict[str, Any]:
    """Return common keyword arguments for file range specification from parsed arguments."""

    return _args_to_kwargs(args, keys)


def get_common_graph_kwargs(args: Namespace,
                            keys: Iterable[str] = [
                                'title',
                                'xlabel',
                                'ylabel',
                                'save',
                                'dpi',
                                'transparent',
                                'show',
                            ],
                            ) -> Dict[str, Any]:
    """Return common keyword arguments for graph specification from parsed arguments."""

    return _args_to_kwargs(args, keys)


def _args_to_kwargs(args: Namespace,
                    keys: Iterable[str],
                    ) -> Dict[str, Any]:
    """Create a dict from a Namespace, keeping selected keys.

    The args object should typically be a parsed `ArgumentParser`.
    We transmute it into a dict and get any keys that are in the set.
    Missing keys are skipped.

    """

    args = vars(args)
    return {k: v for k, v in args.items() if k in keys}
