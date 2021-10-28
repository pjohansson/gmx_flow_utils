#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import numpy as np
import textwrap

from argparse import ArgumentParser
from gmx_flow import read_data


def parse_type_or_none(value, as_type):
    """Return a parsed value or `None` if the input is the string 'none'."""

    if value.lower() == 'none':
        return None 
    else:
        return as_type(value)


def parse_float_or_none(value):
    """Return a parsed float or `None` if the input is the string 'none'."""

    return parse_type_or_none(value, float)


def get_label_legend(label, format):
    """Return a legend entry for a given data label."""

    label = label.upper()

    if (label == 'M') and (format == 'GMX_FLOW_1'):
        return "m"
    elif (label == 'M') and (format == 'GMX_FLOW_2'):
        return r"$\rho$"
    elif label == 'FLOW':
        return r"$(u^2 + v^2)^{1/2}$" 
    else:
        return label.lower()


def add_colorbar_axis(ax, position="right", size="8%", pad=0.10, **kwargs):
    """Add and return a colorbar `Axes` besides the input `Axes`."""

    from mpl_toolkits.axes_grid1 import make_axes_locatable

    divider = make_axes_locatable(ax)

    cax = divider.append_axes(position, size=size, pad=pad, **kwargs)
    fig = ax.get_figure()
    fig.add_axes(cax)

    return cax


def add_flow_magnitude(flow):
    """Add the flow magnitude to the dict and return it."""

    U = flow['U']
    V = flow['V']

    flow['flow'] = np.sqrt(U**2 + V**2)

    return flow


def apply_clim(flow, clim, label):
    if clim == None:
        return flow
    
    cmin, cmax = clim

    if cmin == None:
        cmin = -np.inf
    
    if cmax == None:
        cmax = np.inf
    
    inds = (flow[label] >= cmin) & (flow[label] <= cmax)

    for l in flow.keys():
        flow[l] = flow[l][inds]
    
    return flow


def decorate_graph(func):
    """Decorator which sets up Axes for figure drawing functions.

    Args:
        func: Function to decorate (see below for requirements)
    
    Returns:
        (fig, ax): Tuple with created and/or used `Figure` and `Axes`

    Functions which are decorated with this function should:

     * Accept the drawing `Axes` object as their first positional argument
     * Return a `ScalarMappable` to be used for `ColorBar` creation
       (if applicable)
     * Additional positional and keyword arguments not used by the decorator
       are forwarded to the decorated function. 
       
    If both the decorator and decorated functions share keyword arguments,
    the decorator will not forward them. Such arguments can be forwarded
    using the `extra_kwargs` keyword argument.
    
    The decorator by default creates a new `Figure` and `Axes` to draw in.
    An already created `Axes` can be supplied with the `use_ax` keyword 
    argument. 
    
    """

    def inner(
            *func_args, 
            use_ax=None,
            title=None,
            xlabel=None,
            ylabel=None,
            xlim=(None, None),
            ylim=(None, None),
            axis=None,
            colorbar=False,
            colorbar_label=None,
            colorbar_axis_kwargs={},
            dpi=None,
            show=True,
            save=None,
            tight_layout=False,
            transparent=False,
            extra_kwargs={},
            **func_kwargs):
        if use_ax:
            ax = use_ax
            fig = ax.get_figure()
        else:
            fig, ax = plt.subplots(dpi=dpi)

        if colorbar:
            cax = add_colorbar_axis(ax, **colorbar_axis_kwargs)

        sm = func(ax, *func_args, **extra_kwargs, **func_kwargs)

        if axis:
            ax.axis(axis)

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        if colorbar:
            plt.colorbar(sm, label=colorbar_label, cax=cax)

        if tight_layout and (not use_ax):
            fig.tight_layout()

        if save and (not use_ax):
            plt.savefig(save, transparent=transparent)

        if show and (not use_ax):
            plt.show()

        return fig, ax
    
    return inner


@decorate_graph
def draw_flow(
        ax,
        flow, 
        info, 
        color_label, 
        arrow_color=None,
        scale=None,
        width=None,
        vlim=None,
        ):
    xs = flow['X']
    ys = flow['Y']
    us = flow['U']
    vs = flow['V']
    args = [xs, ys, us, vs]

    if color_label.lower() != 'none':
        color = flow[color_label]
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

    flow, info = read_data(args.path)

    flow = apply_clim(flow, args.xlim, 'X')
    flow = apply_clim(flow, args.ylim, 'Y')

    if args.color_label.lower() == 'flow':
        flow = add_flow_magnitude(flow)
    
    if args.cutoff != None:
        flow = apply_clim(flow, [args.cutoff, None], args.cutoff_label)
    
    ax_kwargs = {
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
        'colorbar': (args.color_label != 'none') and args.show_colorbar,
        'colorbar_label': get_label_legend(args.color_label, info['format']),
    }

    draw_flow(
        flow, info, args.color_label, 
        scale=args.scale, width=args.width, 
        arrow_color=args.arrow_color, vlim=args.vlim,
        **ax_kwargs, **cbar_kwargs)