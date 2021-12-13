#!/usr/bin/env python3

import gmx_flow
import os

from argparse import ArgumentParser
from gmx_flow import read_flow, write_flow, GmxFlowVersion
from gmx_flow.flow import convert_gmx_flow_1_to_2
from gmx_flow.utils import backup_file, get_files_from_range
from sys import stderr


if __name__ == '__main__':
    parser = ArgumentParser(
        description="""Convert flow field maps from `GMX_FLOW_1` to `GMX_FLOW_2`.

            This changes the `M` field to hold the mass density inside bins
            instead of the total mass inside of them. To do this conversion
            a width, or depth, of the maps must be supplied.

            Paths are constructed using the pattern "{base}{:05d}.{extension}"
            for a given input and output `base` and flow field map index.

            All flow fields must have the same grid shape and are also assumed to share
            origin and bin sizes. They should the in the `GMX_FLOW` file format, supported
            by the `gmx_flow` module.

            """,
        epilog="""Copyright Petter Johansson and contributors (2020).

            Distributed freely under the Blue Oak license
            (https://blueoakcouncil.org/license/1.0.0).

            """)

    parser.add_argument('base',
                        type=str, metavar='BASE',
                        help="base path for files to convert")
    parser.add_argument('output_base',
                        type=str, metavar='BASE',
                        help='base path for converted files')
    parser.add_argument('width',
                        type=float, metavar='WIDTH',
                        help="width of 2D system, used to compute the bin volume")

    parser.add_argument('-b', '--begin',
                        type=int, default=1, metavar='INT',
                        help='index of first file to read (default: %(default)s)')
    parser.add_argument('-e', '--end',
                        type=int, default=None, metavar='INT',
                        help='index of last file to read (default: inf)')
    parser.add_argument('--ext',
                        type=str, default='dat',
                        help='extension for files (default: %(default)s)')
    parser.add_argument('-q', '--quiet',
                        action='store_true',
                        help="be less loud and noisy")

    args = parser.parse_args()

    num_files = 0
    num_already_converted = 0

    for fn, fnout in get_files_from_range(
            args.base,
            output_base=args.output_base,
            begin=args.begin,
            end=args.end,
            ext=args.ext):
        flow = read_flow(fn)

        if flow.version == GmxFlowVersion(1):
            flow = convert_gmx_flow_1_to_2(flow, args.width)
        else:
            num_already_converted += 1

        backup_file(fnout)
        write_flow(fnout, flow)

        num_files += 1

    if (num_files == 0) and (not args.quiet):
        stderr.write("warning: no files matching `{}{:05}.{}`, ... found\n".format(
            args.base, args.begin, args.ext
        ))

    if (num_already_converted > 0) and (not args.quiet):
        stderr.write("note: {}/{} files were already in the `{}` format\n".format(
            num_already_converted, num_files, 'GMX_FLOW_2',
        ))
