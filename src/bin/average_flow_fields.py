#!/usr/bin/env python3

import argparse
import os
import textwrap

from argparse import ArgumentParser

from gmx_flow import read_flow, write_flow
from gmx_flow.flow import average_data
from gmx_flow.utils import backup_file


def get_files_from_range(args):
    """Yield files from a range along with the output destination."""

    def get_filename(base, i):
        return "{}{:05d}.{}".format(base, i, args.ext)

    def get_output(i):
        if args.output != None:
            return args.output
        else:
            return get_filename(args.outbase, i)

    if args.outbase == None and args.output == None:
        parser.error(
            'neither \'outbase\' or \'--output\' was specified for output')

    i = args.begin
    n = 1
    fn = get_filename(args.base, i)

    filenames = []

    while os.path.exists(fn) and (args.end == None or i <= args.end):
        filenames.append(fn)

        if args.num != None and len(filenames) == args.num:
            yield filenames, get_output(n)

            n += 1
            filenames = []

        i += 1
        fn = get_filename(args.base, i)

    if args.num == None and filenames != []:
        yield filenames, get_output(n)


def get_files_from_list(args):
    """Yield the list of given files and the output."""

    yield args.files, args.output


def print_file_info(files, fnout, verbosity_level):
    """Print information about the averaging to stdout."""

    if len(files) == 1:
        print(
            "averaging {} file ['{}'] -> '{}'".format(len(files), files[0], fnout))
    elif len(files) == 2:
        print("averaging {} files ['{}', '{}'] -> '{}'".format(
            len(files), files[0], files[1], fnout))
    elif len(files) > 2:
        if verbosity_level == 1:
            file_list = "'{}', ..., '{}'".format(files[0], files[-1])
        elif verbosity_level > 1:
            file_list = ', '.join(files)

        print("averaging {} files [{}] -> '{}'".format(
            len(files), file_list, fnout))


if __name__ == '__main__':
    parser = ArgumentParser(
        description=textwrap.dedent("""
            Average flow field files.

            All flow fields must have the same grid shape
            and are also assumed to share origin and bin sizes.
            They should the in the `GMX_FLOW` file format,
            supported by the `gmx_flow` module.
            """),
        epilog=textwrap.dedent("""
            Copyright Petter Johansson and contributors (2020).

            Distributed freely under the Blue Oak license
            (https://blueoakcouncil.org/license/1.0.0).
            """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        dest='subcommand', required=True,
        title='subcommands',
        description='Sub-commands for input file selection.')

    parser_files = subparsers.add_parser(
        'files',
        description="Average a given set of flow field files.",
        help='average a list of flow field files',
    )
    parser_files.add_argument(
        'files', type=str, nargs='+',
        help='list of flow field files to average',
    )
    parser_files.add_argument(
        'output', type=str,
        help='file to write average into',
    )

    parser_range = subparsers.add_parser(
        'range',
        description=textwrap.dedent("""
            Average a sequential range of flow field files.

            Files are assumed to have paths of the format '{}{:05d}.dat',
            i.e. 'flow_00001.dat', 'flow_00002.dat', etc. The script looks for all matching
            files in this format, starting from the numerical index 1 (can be changed
            with the '-b' flag) until no more can be found (or until an optional maximum
            index set with the '-e' flag).

            The flow fields in these files are averaged and written either to corresponding
            files starting with the given output base of the same for, i.e. 'out_00001.dat',
            'out_00002.dat', etc., or to a single file speficied with the '-o' flag.

            By default, all the found files are averaged and written into a single output
            file. The size of the averaging window can be set with the '-n' flag. If this
            is non-zero, this is the procedure (with '-n=5' in this example):

                ['flow_00001.dat', 'flow_00002.dat', ..., 'flow_00005.dat'] -> 'avg_00001.dat'
                ['flow_00006.dat', 'flow_00007.dat', ..., 'flow_00010.dat'] -> 'avg_00002.dat'
                ['flow_00011.dat', 'flow_00015.dat', ..., 'flow_00015.dat'] -> 'avg_00003.dat'
                ['flow_00016.dat', 'flow_00020.dat', ..., 'flow_00020.dat'] -> 'avg_00004.dat'
            """),
        help=r"average a sequential list "
             r"('flow_00001.dat', 'flow_00002.dat', ...)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser_range.add_argument(
        'base',
        type=str,
        help='base of input files')
    parser_range.add_argument(
        'outbase',
        type=str, nargs='?',
        help='base of output files (unless \'-o\' is supplied)')
    parser_range.add_argument(
        '-o', '--output',
        type=str, default=None, metavar='PATH',
        help='write the averaged data into this file (replaces \'outbase\')')
    parser_range.add_argument(
        '-n', '--num',
        type=int, default=None, metavar='INT',
        help='number of files to average over (default: all files in range)')
    parser_range.add_argument(
        '-b', '--begin',
        type=int, default=1, metavar='INT',
        help='index of first file to read (default: %(default)s)')
    parser_range.add_argument(
        '-e', '--end',
        type=int, default=None, metavar='INT',
        help='index of last file to read (default: inf)')
    parser_range.add_argument(
        '--ext',
        type=str, default='dat', metavar='EXT',
        help='extension for files (default: %(default)s)')

    # set the function used to get the filenames depending on
    # which subparser is selected at runtime. there's probably
    # a better way to check for this. TODO: find it
    parser_files.set_defaults(get_filenames=get_files_from_list)
    parser_range.set_defaults(get_filenames=get_files_from_range)

    parser_files.add_argument(
        '-v', '--verbose',
        action='count',
        help='be loud and noisy')
    parser_range.add_argument(
        '-v', '--verbose',
        action='count',
        help='be loud and noisy')

    args = parser.parse_args()

    # see above comment
    for files, fnout in args.get_filenames(args):
        if files != []:
            if args.verbose != None and args.verbose > 0:
                print_file_info(files, fnout, args.verbose)

            flow_fields = [read_flow(fn) for fn in files]
            avg_flow = average_data(flow_fields)

            backup_file(fnout)
            write_flow(fnout, avg_flow)
