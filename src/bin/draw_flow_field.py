#!/usr/bin/env python3

import matplotlib.pyplot as plt

from argparse import ArgumentParser
from gmx_flow import read_data

def get_label_description(label, format):
    label = label.upper()

    if (label == 'M') and (format == 'GMX_FLOW_1'):
        return "m"
    elif (label == 'M') and (format == 'GMX_FLOW_2'):
        return r"$\rho$"
    else:
        return label.lower()

def add_colorbar_axis(ax, position="right", size="8%", pad=0.10, **kwargs):
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    divider = make_axes_locatable(ax)

    cax = divider.append_axes(position, size=size, pad=pad, **kwargs)
    fig = ax.get_figure()
    fig.add_axes(cax)

    return cax

def draw_flow(flow, info, label, show_colorbar=True):
    xs = flow['X']
    ys = flow['Y']
    values = flow[label]

    bins = info['shape']

    fig, ax  = plt.subplots()

    # hist2d returns its scalar mappable data in its third argument,
    # which is then used to fill the colorbar mapping
    _, _, _, sm = ax.hist2d(xs, ys, weights=values, bins=bins)

    ax.axis('scaled')
    ax.set_xlabel('x')
    ax.set_ylabel('y')

    if show_colorbar:
        data_label = get_label_description(label, info['format'])
        cax = add_colorbar_axis(ax)

        plt.colorbar(sm, label=data_label, cax=cax)

    fig.tight_layout()

    plt.show()


if __name__ == '__main__':
    parser = ArgumentParser(
            description="""Draw flow field data in `GMX_FLOW` format.

            """,
            epilog="""Copyright Petter Johansson and contributors (2020-2021). 

            Distributed freely under the Blue Oak license 
            (https://blueoakcouncil.org/license/1.0.0).

            """)

    parser.add_argument('base', 
            type=str, metavar='BASE',
            help="base path for files to convert")
    parser.add_argument('-l', '--label', 
            default='M', choices=['M', 'U', 'V'],
            help='data label to draw')

    args = parser.parse_args()

    flow, info = read_data(args.base)
    draw_flow(flow, info, args.label)
