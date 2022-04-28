#!/usr/bin/env python3

import argparse
import itertools
import numpy as np
import textwrap

from argparse import ArgumentParser
from matplotlib.axes import Axes

from gmx_flow import read_flow, GmxFlow
from gmx_flow.utils import (
    decorate_graph,
    get_files_or_range,
    loop_items,
)
from gmx_flow.utils.argparse import (
    add_common_graph_args,
    add_common_range_args,
    get_common_graph_kwargs,
    get_common_range_kwargs,
)
from gmx_flow.utils.fileio import gen_output_file_range


def print_item(item: tuple[str, str | None]) -> str:
    match item:
        case fn, None:
            return f"{fn}"
        case fn, fnout:
            return f"{fn} (saving as '{fnout}')"


@decorate_graph
def draw_flow(
        ax: Axes,
        flow: GmxFlow,
        color_label: str,
        colormap: str,
        arrow_color: np.ndarray | str | None = None,
        scale: float | None = None,
        width: float | None = None,
        vlim: tuple[float | None, float | None] = (None, None),
):
    xs = flow.x
    ys = flow.y
    us = flow.u
    vs = flow.v
    args = [xs, ys, us, vs]

    if color_label.lower() != 'none':
        color = flow.data[color_label]
        args.append(color)

    return ax.quiver(
        *args,
        color=arrow_color,
        clim=vlim,
        cmap=colormap,
        pivot='middle',
        scale=scale,
        width=width,
    )


if __name__ == '__main__':
    parser = ArgumentParser(
        description=textwrap.dedent("""
            Draw 2D vector flow field in `GMX_FLOW` format.

            Available data labels for coloring:

             - M: mass density
             - U: flow velocity along X
             - V: flow velocity along Y
             - flow: flow magnitude (sqrt(U^2 + V^2))
             - T: temperature (only for SPC/E water)

            """),
        epilog=textwrap.dedent("""
            Copyright Petter Johansson and contributors (2020-2021).

            Distributed freely under the Blue Oak license
            (https://blueoakcouncil.org/license/1.0.0).

            """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        'path',
        help="path to flow field data file")
    parser.add_argument(
        '-c', '--cutoff',
        default=None, type=float, metavar='MIN',
        help="remove bins with `--cutoff-label` less than this")
    parser.add_argument(
        '--cutoff-label',
        default='M', choices=['M', 'U', 'V', 'flow', 'T'],
        help="data label to use with `--cutoff` (default: %(default)s)")
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help="be less loud and noisy")

    parser_arrows = parser.add_argument_group('arrow options')
    parser_arrows.add_argument(
        '-l', '--label',
        dest='color_label',
        default='flow', choices=['none', 'M', 'U', 'V', 'flow', 'T'],
        help='data label to color arrows with')
    parser_arrows.add_argument(
        '--arrow-color',
        default="#3182bd", type=str, metavar='COLOR',
        help="color for arrows (if `--label` is none)")
    parser_arrows.add_argument(
        '--scale',
        default=None, type=float,
        help="scaling for arrows (lower -> longer arrows)")
    parser_arrows.add_argument(
        '--width',
        default=None, type=float,
        help="width of arrows")

    parser_graph = add_common_graph_args(parser, add_colormap=True)
    parser_range = add_common_range_args(parser, outext='png', add_outext=True)

    args = parser.parse_args()

    kwargs_graph = get_common_graph_kwargs(args, axis='scaled')
    kwargs_range = get_common_range_kwargs(args)

    if args.outext == None:
        kwargs_range_output = kwargs_range.copy()
    else:
        kwargs_range_output = kwargs_range | {'ext': args.outext}

    fns = get_files_or_range(args.path, **kwargs_range)

    if len(fns) == 1 or args.save == None:
        fn_tuples = zip(fns, itertools.repeat(args.save))
    else:
        fn_tuples = zip(
            fns,
            gen_output_file_range(args.save, **kwargs_range_output)
        )

    for fn, fnout in loop_items(fn_tuples, formatter=print_item, quiet=args.quiet):
        flow = read_flow(fn)
        flow.set_xlim(*args.xlim)
        flow.set_ylim(*args.ylim)

        if args.cutoff != None:
            flow.set_clim(args.cutoff, None, args.cutoff_label)

        kwargs_graph.update({'save': fnout})
        if kwargs_graph.get('colorbar_label', None) == None:
            kwargs_graph.update(
                {'colorbar_label': flow.units.get(args.color_label, None)})

        draw_flow(
            flow,
            args.color_label,
            scale=args.scale,
            width=args.width,
            arrow_color=args.arrow_color,
            colormap=args.colormap,
            vlim=args.vlim,
            **kwargs_graph,
        )
