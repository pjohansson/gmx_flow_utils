#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import numpy as np
import textwrap

from argparse import ArgumentParser
from matplotlib.axes import Axes
from typing import Optional, Tuple

from gmx_flow import read_flow, GmxFlow
from gmx_flow.flow import supersample
from gmx_flow.utils.argparse import parse_float_or_none
from gmx_flow.utils.graph import decorate_graph


@decorate_graph
def draw_flow(ax: Axes,
              flow: GmxFlow,
              label: str,
              vlim: Optional[Tuple[float, float]] = None):
    xs = flow.x.ravel()
    ys = flow.y.ravel()
    values = flow.data[label].ravel()

    bins = flow.shape

    try:
        vmin, vmax = vlim
    except:
        vmin = None
        vmax = None

    # hist2d returns its scalar mappable data in its fourth argument,
    # which is then used to fill the colorbar mapping
    _, _, _, sm = ax.hist2d(
        xs, ys,
        weights=values, bins=bins,
        vmin=vmin, vmax=vmax)

    return sm


if __name__ == '__main__':
    parser = ArgumentParser(
        description=textwrap.dedent("""
            Draw 1D flow field data in `GMX_FLOW` format.

            Available data labels:

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
    parser.add_argument('-l', '--label',
                        default='M', choices=['M', 'U', 'V', 'flow', 'T'],
                        help='data label to draw')
    parser.add_argument('-c', '--cutoff',
                        default=None, type=float,
                        help="remove bins with `--cutoff-label` less than this")
    parser.add_argument('--cutoff-label',
                        default='M', choices=['M', 'U', 'V', 'flow', 'T'],
                        help="data label to use with `--cutoff` (default: %(default)s)")
    parser.add_argument('--supersample',
                        default=1, type=int, metavar='N',
                        help="supersample data by a given factor")
    parser.add_argument('--vlim',
                        type=parse_float_or_none, nargs=2, metavar=('VMIN', 'VMAX'),
                        help="limits of color axis")

    parser_graph = parser.add_argument_group('graph options')
    parser_graph.add_argument('--xlim',
                              type=parse_float_or_none, nargs=2, metavar=('XMIN', 'XMAX'),
                              help="graph limits along x axis")
    parser_graph.add_argument('--ylim',
                              type=parse_float_or_none, nargs=2, metavar=('YMIN', 'YMAX'),
                              help="graph limits along y axis")
    parser_graph.add_argument('--title',
                              type=str, default=None,
                              help="graph title")
    parser_graph.add_argument('--xlabel',
                              type=str, default='x',
                              help="x axis label")
    parser_graph.add_argument('--ylabel',
                              type=str, default='y',
                              help="y axis label")
    parser_graph.add_argument('--save',
                              default=None, type=str, metavar='PATH',
                              help="save figure to path")
    parser_graph.add_argument('--dpi',
                              default=None, type=int,
                              help="dpi of figure")
    parser_graph.add_argument('--transparent',
                              action='store_true',
                              help="save figure with transparent background")
    parser_graph.add_argument('--noshow',
                              action='store_false', dest='show',
                              help="do not show figure window")
    parser_graph.add_argument('--nocolorbar',
                              action='store_false', dest='show_colorbar',
                              help="do not show color bar")

    args = parser.parse_args()

    flow = read_flow(args.path)

    if args.supersample > 1:
        flow = supersample(flow, args.supersample, labels=[
            args.label, args.cutoff_label])

    if args.cutoff != None:
        flow.set_clim(args.cutoff, None, args.cutoff_label)

    ax_kwargs = {
        'xlim': args.xlim,
        'ylim': args.ylim,
        'title': args.title,
        'xlabel': args.xlabel,
        'ylabel': args.ylabel,
        'axis': 'scaled',
        'tight_layout': True,
        'show': args.show,
        'save': args.save,
        'transparent': args.transparent,
        'dpi': args.dpi,
    }

    cbar_kwargs = {
        'colorbar': args.show_colorbar,
        'colorbar_label': flow.units[args.label],
    }

    draw_flow(flow, args.label, vlim=args.vlim,
              **ax_kwargs, **cbar_kwargs)
