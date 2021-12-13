#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import numpy as np
import textwrap

from argparse import ArgumentParser
from matplotlib.axes import Axes
from typing import Tuple, Optional, Union

from gmx_flow import read_flow, GmxFlow
from gmx_flow.utils.argparse import parse_float_or_none, add_common_graph_args, get_common_graph_kwargs
from gmx_flow.utils import decorate_graph


@decorate_graph
def draw_flow(
        ax: Axes,
        flow: GmxFlow,
        color_label: str,
        arrow_color: Union[Optional[str], np.ndarray] = None,
        scale: Optional[float] = None,
        width: Optional[float] = None,
        vlim: Optional[Tuple[float, float]] = None,
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
        color=arrow_color, clim=vlim, pivot='middle',
        scale=scale, width=width)


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

    parser.add_argument('path',
                        help="path to flow field data file")
    parser.add_argument('-c', '--cutoff',
                        default=None, type=float,
                        help="remove bins with `--cutoff-label` less than this")
    parser.add_argument('--cutoff-label',
                        default='M', choices=['M', 'U', 'V', 'flow', 'T'],
                        help="data label to use with `--cutoff` (default: %(default)s)")

    parser_arrows = parser.add_argument_group('arrow options')
    parser_arrows.add_argument('-l', '--label',
                               dest='color_label',
                               default='flow', choices=['none', 'M', 'U', 'V', 'flow', 'T'],
                               help='data label to color arrows with')
    parser_arrows.add_argument('--arrow-color',
                               default="#3182bd", type=str,
                               help="color for arrows (if `--label` is none)")
    parser_arrows.add_argument('--scale',
                               default=None, type=float,
                               help="scaling for arrows (lower -> longer arrows)")
    parser_arrows.add_argument('--width',
                               default=None, type=float,
                               help="width of arrows")
    parser_arrows.add_argument('--vlim',
                               type=parse_float_or_none, nargs=2, metavar=('VMIN', 'VMAX'),
                               help="limits of color axis")

    parser_graph = add_common_graph_args(parser)
    parser_graph.add_argument('--nocolorbar',
                              action='store_false', dest='show_colorbar',
                              help="do not show color bar")

    args = parser.parse_args()

    flow = read_flow(args.path)
    flow.set_xlim(*args.xlim)
    flow.set_ylim(*args.ylim)

    if args.cutoff != None:
        flow.set_clim(args.cutoff, None, args.cutoff_label)

    kwargs_graph = get_common_graph_kwargs(args)
    kwargs_graph['axis'] = 'scaled'
    kwargs_graph['tight_layout'] = True

    kwargs_cbar = {
        'colorbar': (args.color_label != 'none') and args.show_colorbar,
        'colorbar_label': flow.units[args.color_label],
    }

    draw_flow(
        flow, args.color_label,
        scale=args.scale, width=args.width,
        arrow_color=args.arrow_color, vlim=args.vlim,
        **kwargs_graph,
        **kwargs_cbar)
