#!/usr/bin/env python3

import argparse
import textwrap

from argparse import ArgumentParser
from collections.abc import Callable, Sequence

from gmx_flow import read_flow, write_flow
from gmx_flow.flow import average_data
from gmx_flow.utils import backup_file, loop_items
from gmx_flow.utils.argparse import add_common_range_args, get_common_range_kwargs
from gmx_flow.utils.fileio import gen_output_file_range, gen_grouped_files


def get_formatter(verbose: bool) -> Callable[[tuple[Sequence[str], str]], str]:
    def inner(input: tuple[Sequence[str], str]) -> str:
        match input:
            case [], fnout:
                return f"[] -> {fnout}"
            case [fn], fnout:
                return f"['{fn}'] -> '{fnout}'"
            case [fn1, fn2], fnout:
                return f"['{fn1}, {fn2}'] -> '{fnout}'"
            case files, fnout:
                if verbose:
                    file_list = ', '.join(files)
                else:
                    file_list = "'{}', ..., '{}'".format(files[0], files[-1])

                return f"[{file_list}] -> '{fnout}'"

    return inner


if __name__ == '__main__':
    parser = ArgumentParser(
        description=textwrap.dedent("""
            Average flow field files.

            Files for a given range are assumed to have paths of the format '{}{:05d}.dat',
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

            All flow fields must have the same grid shape and are assumed to share origin 
            and bin sizes. They should the in the `GMX_FLOW` file format, supported by the 
            `gmx_flow` module.
            """),
        epilog=textwrap.dedent("""
            Copyright Petter Johansson and contributors (2020).

            Distributed freely under the Blue Oak license
            (https://blueoakcouncil.org/license/1.0.0).
            """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        'base',
        type=str, nargs='?', 
        help='base of input files')
    parser.add_argument(
        'outbase',
        type=str, nargs='?', 
        help='base of output files (unless \'-o\' is supplied)')
    parser.add_argument(
        '-f', '--files', 
        nargs='+', metavar='PATH', default=None,
        help="list of files to average and write to `--output`")
    parser.add_argument(
        '-o', '--output',
        type=str, default=None, metavar='PATH',
        help='write the averaged data into this file (replaces \'outbase\')')
    parser.add_argument(
        '-n', '--num',
        type=int, default=None, metavar='INT',
        help='number of files to average over (default: all files in range)')

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='print averaged file information')
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='do not print anything')

    add_common_range_args(
        parser,
        add_backup=True,
        add_outext=True,
        add_outbegin=True,
    )

    args = parser.parse_args()

    kwargs_range = get_common_range_kwargs(args)
    kwargs_range_output = kwargs_range | {'begin': args.out_begin}

    if args.outext != None:
        kwargs_range_output = kwargs_range | {'ext': args.outext}

    f = get_formatter(args.verbose)

    try:
        match args.base, args.outbase, args.files, args.output:
            case None, _, None, _:
                raise ValueError("no files where specified with `base` or `--files`")
            case str(_), None, _, _:
                raise ValueError("missing base for output files (`outbase`)")
            case str(base), str(outbase), _, _:
                fns = list(zip(
                    gen_grouped_files(base, args.num, **kwargs_range),
                    gen_output_file_range(outbase, **kwargs_range_output)
                ))
            case _, _, [*files], str(fnout):
                fns = [(files, fnout)]
            case _, _, _, None:
                raise ValueError("no output file specified with `--output`")
            case _:
                raise ValueError("no files where specified with `base` or `--files`")
    except ValueError as exc:
        print(f"error: {exc}")
        exit(1)

    for files, fnout in loop_items(fns, formatter=f, quiet=args.quiet):
        if files == []:
            continue 

        flow_fields = [read_flow(fn) for fn in files]
        avg_flow = average_data(flow_fields)

        if avg_flow == None:
            print(f"error: could not average files {f((files, fnout))}")
            exit(1)

        if args.backup:
            backup_file(fnout)

        write_flow(fnout, avg_flow)
