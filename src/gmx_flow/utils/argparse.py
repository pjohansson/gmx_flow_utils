"""Utilities for working with `ArgumentParser` parsers."""

from argparse import ArgumentParser, _ArgumentGroup, Namespace
from collections.abc import Iterable, Sequence
from typing import Any, TypeVar

# From what I understand this is the only way to declare a generic `type` variable
# to use for the type hinting
T = TypeVar('T')


def parse_float_or_none(value: str) -> float | None:
    """Return a parsed float or `None` if the input is the string 'none'."""

    return _parse_type_or_none(value, float)


def _parse_type_or_none(value: str, as_type: T) -> T | None:
    """Return a parsed value or `None` if the input is the string 'none'."""

    if value.lower() == 'none':
        return None
    else:
        return as_type(value)


def add_common_range_args(
    parser: ArgumentParser,
    use_group: _ArgumentGroup | None = None,
    begin: int = 1,
    end: int | None = None,
    ext: str | Sequence[str] = ['dat.gz', 'dat'],
    dt: float = 1.,
    outext: str | None = None,
    outbegin: int = 1,
    add_backup: bool = False,
    add_outext: bool = False,
    add_outbegin: bool = False,
    add_time: bool = False,
) -> _ArgumentGroup:
    """Add common keyword arguments for file range specification.

    By default the new group is created by calling the `add_argument_group`
    method to the given `parser`. They can instead be added to a given
    group by supplying one with `use_group`. If so, no new argument group
    is created.

    The created argument group is returned.

    """

    if use_group is None:
        parser_range = parser.add_argument_group('range options')
    else:
        parser_range = use_group

    parser_range.add_argument(
        '-b', '--begin',
        type=int, default=begin, metavar='INT',
        help='index of first file to read (default: %(default)s)')
    parser_range.add_argument(
        '-e', '--end',
        type=int, default=end, metavar='INT',
        help='index of last file to read')
    parser_range.add_argument(
        '--ext',
        type=str, default=ext,
        help='extension for files (default: %(default)s)')

    if add_time:
        parser_range.add_argument(
            '--dt',
            type=float, default=dt, metavar='DT',
            help="time between files in range (default: %(default)s)",
        )

    if add_outext:
        parser_range.add_argument(
            '--outext',
            type=str, default=outext, metavar='EXT',
            help='extension for output files (default: %(default)s)')

    if add_outbegin:
        parser_range.add_argument(
            '--out-begin',
            type=int, default=outbegin, metavar='INT',
            help="index of first output file (default: %(default)s)",
        )

    if add_backup:
        parser_range.add_argument(
            '--nobackup',
            action='store_false', dest='backup',
            help="overwrite existing files without backing them up"
        )

    return parser_range


def add_common_graph_args(
    parser: ArgumentParser | None,
    use_group: _ArgumentGroup | None = None,
    title: str = '',
    xlabel: str = r'$x$',
    ylabel: str = r'$y$',
    xlim: tuple[float | None, float | None] = (None, None),
    ylim: tuple[float | None, float | None] = (None, None),
    vlim: tuple[float | None, float | None] = (None, None),
    save: str | None = None,
    dpi: int | None = None,
    colormap: str = 'viridis',
    linewidth: float | None = None,
    add_axis_limits: bool = True,
    add_labels: bool = True,
    add_save: bool = True,
    add_colormap: bool = False,
    add_line: bool = False,
) -> _ArgumentGroup:
    """Add common keyword arguments for graph specification.

    By default the new group is created by calling the `add_argument_group`
    method to the given `parser`. They can instead be added to a given
    group by supplying one with `use_group`. If so, no new argument group
    is created.

    The created argument group is returned.

    """

    import matplotlib.pyplot as plt

    if use_group is None:
        parser_graph = parser.add_argument_group('graph options')
    else:
        parser_graph = use_group

    if add_labels:
        parser_graph.add_argument(
            '--title',
            type=str, default=title,
            help="graph title")
        parser_graph.add_argument(
            '--xlabel',
            type=str, default=xlabel,
            help="x axis label")
        parser_graph.add_argument(
            '--ylabel',
            type=str, default=ylabel,
            help="y axis label")

    if add_axis_limits:
        parser_graph.add_argument(
            '--xlim',
            type=parse_float_or_none, default=xlim,
            nargs=2, metavar=('XMIN', 'XMAX'),
            help="graph limits along x axis")
        parser_graph.add_argument(
            '--ylim',
            type=parse_float_or_none, default=ylim,
            nargs=2, metavar=('YMIN', 'YMAX'),
            help="graph limits along y axis")

    if add_colormap:
        parser_graph.add_argument(
            '--vlim',
            type=parse_float_or_none, default=vlim,
            nargs=2, metavar=('VMIN', 'VMAX'),
            help="limits of color bar values")

    if add_line:
        parser_graph.add_argument(
            '--linewidth',
            type=parse_float_or_none, default=linewidth,
            metavar='WIDTH',
            help="width of plotted line")

    if add_save:
        parser_graph.add_argument(
            '--save',
            type=str, default=save, metavar='PATH',
            help="save figure to path")
        parser_graph.add_argument(
            '--dpi',
            type=int, default=dpi,
            help="dpi of figure")
        parser_graph.add_argument(
            '--transparent',
            action='store_true',
            help="save figure with transparent background")

    if add_colormap:
        parser_graph.add_argument(
            '--colormap',
            default=colormap, metavar='CMAP', choices=plt.colormaps(),
            help="colormap for data (default: %(default)s)")
        parser_graph.add_argument(
            '--nocolorbar',
            action='store_false',
            dest='colorbar',
            help="do not show color bar")

    parser_graph.add_argument(
        '--noshow',
        action='store_false', dest='show',
        help="do not show figure window")

    return parser_graph


def get_common_range_kwargs(
    args: Namespace,
    keys: Iterable[str] = ['begin', 'end', 'ext'],
    skip: Iterable[str] = [],
) -> dict[str, Any]:
    """Return common keyword arguments for file range specification from parsed arguments.

    Keys in the `skip` list will be ignored.

    """

    return _args_to_kwargs(args, keys, skip)


def get_common_graph_kwargs(
    args: Namespace,
    keys: Iterable[str] = [
        'title',
        'xlabel',
        'ylabel',
        'xlim',
        'ylim',
        'save',
        'dpi',
        'transparent',
        'show',
        'colorbar',
    ],
    skip: Iterable[str] = [],
    axis: str | None = None,
    tight_layout: bool = True,
    colorbar_label: str | None = None,
) -> dict[str, Any]:
    """Return common keyword arguments for graph specification from parsed arguments.

    By default only the keyword arguments which are consumed by `decorate_graph`
    are included. This excludes arguments like `colormap` and `vlim` since
    they are often used directly when drawing the graph.

    Keys in the `skip` list will be ignored.

    """

    extra_opts = {
        'axis': axis,
        'tight_layout': tight_layout,
        'colorbar_label': colorbar_label,
    }

    return _args_to_kwargs(args, keys, skip) | extra_opts


def _args_to_kwargs(args: Namespace,
                    keys: Iterable[str],
                    skip: Iterable[str] = [],
                    ) -> dict[str, Any]:
    """Create a dict from a Namespace, keeping selected keys.

    For additional security keys can be ignored by supplying them
    in a list with the `skip` keyword argument. This can be useful
    if a standard set of `keys` is supplied but a non-standard
    behavior in which some of those are skipped is needed.

    The args object should typically be a parsed `ArgumentParser`.
    We transmute it into a dict and get any keys that are in the set.
    Missing keys are skipped.

    """

    args_dict = vars(args)

    return {
        k: v for k, v in args_dict.items()
        if (k in keys) and (k not in skip)
    }
