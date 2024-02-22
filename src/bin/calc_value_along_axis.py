#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats

from argparse import ArgumentParser
from typing import Any

from gmx_flow import read_flow
from gmx_flow.utils import decorate_graph, get_files_or_range, loop_items, backup_file
from gmx_flow.utils.argparse import (
    add_common_graph_args,
    add_common_range_args,
    get_common_graph_kwargs,
    get_common_range_kwargs,
    parse_float_or_none,
)


@decorate_graph
def plot_values(ax, xs: np.ndarray, ys: np.ndarray, **kwargs):
    return ax.plot(xs, ys, **kwargs)


def write(path: str, xs: np.ndarray, vs: np.ndarray, axis: str, label: str, units: dict[str, str], backup: bool):
    if backup:
        backup_file(path)

    header = (
        f"Column 0: {axis.lower()} ({units.get(axis)})\n"
        f"Column 1: {label} ({units.get(label)})"
    )

    data = np.zeros((xs.size, 2))
    data[:, 0] = xs
    data[:, 1] = vs

    np.savetxt(path, data, header=header, comments="# ", fmt="%9g")


def update_graph_xylabels(kwargs: dict[str, Any], axis: str, label: str, units: dict[str, str]):
    if kwargs['xlabel'] == '':
        kwargs['xlabel'] = f"{axis.lower()} ({units.get(axis)})"

    if kwargs['ylabel'] == '':
        kwargs['ylabel'] = f"{label} ({units.get(label)})"


def analyze_and_log_data(xs: np.ndarray, vs: np.ndarray, axis: str, label: str, units: dict[str, str]):
    dvdx, _, _, _, stderr = scipy.stats.linregress(xs, vs)
    grad_unit = f"{units.get(label)}/{units.get(axis)}"

    print(f"{'Parameter':12} "
          f"{'Min':>10} "
          f"{'Max':>10} "
          f"{'Mean':>10} "
          f"{'Std. Err.':>10} "
          f"{'Unit':>10}"
          )
    print(f"{'-' * 72}")

    print(f"{axis.lower():12} "
          f"{xs[0]:10.6g} "
          f"{xs[-1]:10.6g} "
          f"{'-':>10} "
          f"{'-':>10} "
          f"{units.get(axis):>10}"
          )

    print(f"{label:12} "
          f"{vs.min():10.6g} "
          f"{vs.max():10.6g} "
          f"{vs.mean():>10.6g} "
          f"{np.sqrt(vs.std()):>10.6g} "
          f"{units.get(label):>10}"
          )

    print(f"{f'grad {label}':12} "
          f"{'-':>10} "
          f"{'-':>10} "
          f"{dvdx:>10.6g} "
          f"{stderr:>10.6g} "
          f"{grad_unit:>10}"
          )


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument(
        'path',
        nargs='+', type=str,
        help="base of range of files, or list of files to analyze",
    )
    parser_opts = parser.add_argument_group('parameter and axis options')
    parser_opts.add_argument(
        '-a', '--axis',
        choices=['X', 'Y'], type=str.upper, default='X',
        help="axis along which to calculate parameter (default: %(default)s)",
    )
    parser_opts.add_argument(
        '-l', '--label',
        choices=['M', 'U', 'V', 'flow', 'T'], default='flow',
        help="label of parameter to calculate along chosen axis (default: %(default)s)",
    )
    parser_opts.add_argument(
        '--multiply-parameter-by',
        type=float, default=1., metavar='VALUE',
        help="optionally multiply the parameter by a given factor",
    )

    parser_cutoff = parser.add_argument_group('cutoff options')
    parser_cutoff.add_argument(
        '-c', '--cutoff',
        default=None, type=float,
        help="remove bins with `--cutoff-label` less than this",
    )
    parser_cutoff.add_argument(
        '--cutoff-label',
        default='M', choices=['M', 'U', 'V', 'flow', 'T'],
        help="data label to use with `--cutoff` (default: %(default)s)",
    )
    parser_cutoff.add_argument(
        '--use-xlim',
        nargs=2, default=(None, None), metavar=('X0', 'X1'),
        type=parse_float_or_none,
        help="limit calculation area along the x axis",
    )
    parser_cutoff.add_argument(
        '--use-ylim',
        nargs=2, default=(None, None), metavar=('Y0', 'Y1'),
        type=parse_float_or_none,
        help="limit calculation area along the y axis",
    )

    parser.add_argument(
        '-o', '--output',
        type=str, default=None, metavar='PATH',
        help="write data to .xvg file",
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
        # Empty string == default value in this script (set from axis/label)
        xlabel='',
        ylabel='',
    )

    args = parser.parse_args()

    kwargs_graph = get_common_graph_kwargs(args)
    kwargs_range = get_common_range_kwargs(args)

    fns = get_files_or_range(*args.path, **kwargs_range)

    ts = args.dt * (args.begin - 1 + np.arange(len(fns)))
    xcom = np.zeros_like(ts)
    ycom = np.zeros_like(ts)

    num_bins = 0
    data = np.zeros(0)
    units = {}

    if args.axis == 'Y':
        index_axis = 0
    else:
        index_axis = 1

    cut_xmin, cut_xmax = args.use_xlim
    cut_ymin, cut_ymax = args.use_ylim

    set_xlim = (cut_xmin != None) or (cut_xmax != None)
    set_ylim = (cut_ymin != None) or (cut_ymax != None)

    for i, fn in enumerate(loop_items(fns, formatter=str, quiet=args.quiet)):
        flow = read_flow(fn)

        if set_xlim:
            flow.set_xlim(cut_xmin, cut_xmax)

        if set_ylim:
            flow.set_ylim(cut_ymin, cut_ymax)

        if i == 0:
            units = flow.units.copy()
            update_graph_xylabels(kwargs_graph, args.axis, args.label, units)

        # Calculate the number of bins along the axis and prepare the array
        # NOTE: This assumes that the grid shape is constant for all flow maps
        if num_bins == 0:
            xs = flow.data[args.axis].mean(index_axis)
            num_bins = xs.size

            # rows in data are: x, v, num_samples
            data = np.zeros((3, num_bins))
            data[0, :] = xs

        if args.cutoff != None:
            if args.axis == 'X':
                dx, _ = flow.spacing
            else:
                _, dx = flow.spacing

            flow.set_clim(args.cutoff, None, args.cutoff_label)
            xs = flow.data[args.axis].ravel()
            vs = flow.data[args.label].ravel()

            xmin = xs.min() - (dx / 2.)
            xmax = xs.max() + (dx / 2.)
            size_x = xmax - xmin

            for x, v in zip(xs, vs):
                xrel = (x - xmin) / size_x
                j = int(np.floor((float(num_bins) * xrel)))

                data[1, j] += v
                data[2, j] += 1.

        else:
            vs = flow.data[args.label].mean(index_axis)
            data[1, :] += vs

    data[1, :] *= args.multiply_parameter_by

    if args.cutoff == None:
        data[1, :] /= float(len(fns))
    else:
        data[1, :] /= data[2, :]

    xs = data[0, :]
    vs = data[1, :]

    if not args.quiet:
        analyze_and_log_data(xs, vs, args.axis, args.label, units)

    if args.output != None:
        write(args.output, xs, vs, args.axis, args.label, units, args.backup)

    plot_values(
        xs, vs,
        **kwargs_graph,
    )
