#!/usr/bin/env python3

import argparse
import textwrap

from argparse import ArgumentParser
from sys import stderr

from gmx_flow import read_flow, write_flow, GmxFlowVersion
from gmx_flow.flow import convert_gmx_flow_1_to_2
from gmx_flow.utils import (
    backup_file,
    loop_items,
)
from gmx_flow.utils.argparse import (
    add_common_range_args,
    get_common_range_kwargs,
)
from gmx_flow.utils.fileio import gen_file_range, gen_output_file_range


def formatter(fn_tuple: tuple[str, str]) -> str:
    fn, fnout = fn_tuple
    return f"{fn} -> {fnout} "


if __name__ == '__main__':
    parser = ArgumentParser(
        description=textwrap.dedent("""
            Convert flow field maps from `GMX_FLOW_1` to `GMX_FLOW_2`.

            This changes the `M` field to hold the mass density inside bins
            instead of the total mass inside of them. To do this conversion
            a width, or depth, of the maps must be supplied.

            Paths are constructed using the pattern "{base}{:05d}.{extension}"
            for a given input and output `base` and flow field map index.

            All flow fields must have the same grid shape and are also assumed to share
            origin and bin sizes. They should the in the `GMX_FLOW` file format, supported
            by the `gmx_flow` module.

            """),
        epilog=textwrap.dedent("""
            Copyright Petter Johansson and contributors (2020).

            Distributed freely under the Blue Oak license
            (https://blueoakcouncil.org/license/1.0.0).
            """),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        'base',
        type=str, metavar='BASE',
        help="base path for files to convert")
    parser.add_argument(
        'output_base',
        type=str, metavar='OUTBASE',
        help='base path for converted files')
    parser.add_argument(
        'width',
        type=float, metavar='WIDTH',
        help="width of 2D system, used to compute the bin volume")

    add_common_range_args(parser, add_backup=True, add_outext=True)

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help="be less loud and noisy")

    args = parser.parse_args()

    kwargs_range = get_common_range_kwargs(args)
    kwargs_range_output = kwargs_range | {'ext': args.outext}

    num_files = 0
    num_previously_converted = 0

    fn_tuples = zip(
        gen_file_range(args.base, **kwargs_range),
        gen_output_file_range(args.output_base, **kwargs_range_output)
    )

    for fn, fnout in loop_items(
        fn_tuples,
        quiet=args.quiet,
        formatter=formatter,
    ):
        flow = read_flow(fn)

        if flow.version == GmxFlowVersion(1):
            flow = convert_gmx_flow_1_to_2(flow, args.width)
        else:
            num_previously_converted += 1

        if args.backup:
            backup_file(fnout)

        write_flow(fnout, flow)

        num_files += 1

    if (num_files == 0) and (not args.quiet):
        stderr.write(
            f"warning: no files matching "
            f"`{args.base}{args.begin:05}.{args.ext}`, ... found"
        )

    if (num_previously_converted > 0) and (not args.quiet):
        stderr.write(
            f"note: {num_previously_converted}/{num_files} files "
            f"were already in the `GMX_FLOW_2` format\n"
        )
