#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

from argparse import ArgumentParser

from gmx_flow import read_flow
from gmx_flow.utils import decorate_graph, get_files_or_range, loop_items, backup_file
from gmx_flow.utils.argparse import (
    add_common_graph_args,
    add_common_range_args,
    get_common_graph_kwargs,
    get_common_range_kwargs,
)


@decorate_graph
def plot_values(ax, xs: np.ndarray, ys: np.ndarray, **kwargs):
    return ax.plot(xs, ys, **kwargs)


def write(path: str, ts: np.ndarray, xs: np.ndarray, ys: np.ndarray, backup: bool):
    if backup:
        backup_file(path)

    header = (
        "Center-of-mass over time\n"
        "Column 0: time\n"
        "Column 1: x\n"
        "Column 2: y"
    )

    data = np.zeros((xs.size, 3))

    data[:, 0] = ts
    data[:, 1] = xs
    data[:, 2] = ys

    np.savetxt(path, data, header=header, comments="# ", fmt="%9g")


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument(
        'path',
        nargs='+', type=str,
        help="base of range of files, or list of files to analyze",
    )
    parser.add_argument(
        '-o', '--output',
        type=str, default=None, metavar='PATH',
        help="write center-of-mass data to .xvg file",
    )
    parser.add_argument(
        '--nobackup',
        action='store_false', dest='backup',
        help="overwrite existing files without backing them up"
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help="be less loud and noisy",
    )

    add_common_range_args(parser, add_time=True)
    add_common_graph_args(
        parser,
        xlabel=r'$t$',
        ylabel='COM',
    )

    args = parser.parse_args()

    kwargs_graph = get_common_graph_kwargs(args, skip=['ylabel'])
    kwargs_range = get_common_range_kwargs(args)

    fns = get_files_or_range(*args.path, **kwargs_range)

    ts = args.dt * (args.begin - 1 + np.arange(len(fns)))
    xcom = np.zeros_like(ts)
    ycom = np.zeros_like(ts)

    for i, fn in enumerate(loop_items(fns, formatter=str, quiet=args.quiet)):
        flow = read_flow(fn)

        xs = flow.x
        ys = flow.y
        ms = flow.mass

        xcom[i] = np.average(xs, weights=ms)
        ycom[i] = np.average(ys, weights=ms)

    if args.output != None:
        write(args.output, ts, xcom, ycom, args.backup)

    kwargs_graph.update({'show': False, 'tight_layout': True})

    fig, (ax1, ax2) = plt.subplots(nrows=2)
    plot_values(
        ts, xcom,
        use_ax=ax1, ylabel=f"{args.ylabel} (x)",
        **kwargs_graph,
    )
    plot_values(
        ts, ycom,
        use_ax=ax2, ylabel=f"{args.ylabel} (y)",
        **kwargs_graph,
    )
    plt.tight_layout(pad=1.15, h_pad=0.2)

    if kwargs_graph['save'] != None:
        plt.savefig(kwargs_graph['save'], transparent=kwargs_graph['transparent'])

    plt.show()
