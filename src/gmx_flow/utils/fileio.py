"""File parsing and backup utilities."""

import itertools
import os
import sys

from collections.abc import Callable, Generator, Iterable, Sequence
from sys import stderr
from typing import Any, TextIO, TypeVar

# different return types from `get_files_from_range`
Path = str
PathWithOutput = tuple[str, str]
Paths = Sequence[str]
PathsWithSingleOutput = tuple[Sequence[str], str]

# combined return type
GetRangePaths = Path | PathWithOutput | Paths | PathsWithSingleOutput


def get_files_or_range(input: str, **kwargs: Any) -> list[str]:
    """If input is files, return as list, else return a range."""

    if os.path.exists(input):
        output_base = kwargs.get('output_base', None)

        if output_base != None:
            return [(input, output_base)]
        else:
            return [input]
    else:
        return list(get_files_from_range(input, **kwargs))


def get_files_from_range(
    *fnbase: str,
    output_base: str | None = None,
    num_per_output: int | None = None,
    begin: int = 1,
    end: int | None = None,
    stride: int = 1,
    ext: str = 'dat',
    outext: str | None = None,
    no_check: bool = False,
) -> Generator[GetRangePaths, None, None]:
    """Yield paths to existing files with given base paths.

    Filenames are constructed using the format `{base}{:05d}.{ext}`,
    i.e. `flow_00001.dat`, `flow_00002.dat`, ...

    Several bases can be supplied, in which case the filenames
    for all bases are verified to exist and returned as a list.
    The generation stops as soon as any generated path does not
    exist.

    Unless specific beginning and end points are specified, the function
    yields all filenames with the given base and numbering starting from
    index 1 until a file with the next larger index is not found.

    Optionally, the filenames can be yielded along with a corresponding
    output path by supplying one with `output_base`. The output paths
    are constructed using the same pattern as the input paths, with the
    same file extension. Example use: convert a set of flow field maps
    and write the results to new files.

    Furthermore, by supplying a number to `num_per_output` we can yield
    a number of input paths along with a single output path. Example use:
    block averaging of N input files, saving the average to new files.


    # Arguments

    fnbase (strs): Given filename base(s) to find and yield files for.

    output_base (str): Given filename base to yield output files for.

    num_per_output (int): Yield this many input files at ones for a single output file.

    begin (int): First index to yield input files for.

    end (int): Last index to yield input files for.

    ext (str): Extension to yield files for.

    outext (str): Extension to yield output files for (default is same as for `ext`).

    no_check (bool): Set to `True` to only create file names, not check for existance.


    # Yields

    fn (str):             input files if only a single base was given
    fns ([str]):          input files for each base if multiple bases were given
    fn, fnout (str, str): input and output files if `output_base` != `None`
    fns, fnout ([str], str): list of input files for a single output file
                             if `output_base` and `num_per_output` != `None`
    [fns1, fns2, ...], fnout ([[str]], str):
                          yielding multiple files for multiple bases, along with
                          an output file. fns1 is the files for base1, fns2 for
                          base2, etc.

    # Examples

    Read a set of files with filenames `flow_00001.dat`, `flow_00002.dat`, ...

    ```
    for fn in get_files_from_range('flow_'):
        print(fn) # `flow_00001.dat`
                  # `flow_00002.dat`
                  # ... until no more files are found for the pattern
    ```

    Read files in a range of indices 5 to 10 (inclusive):

    ```
    for fn in get_files_from_range('flow_', begin=5, end=10):
        print(fn) # `flow_00005.dat`
                  # `flow_00006.dat`
                  # ...
                  # `flow_00010.dat`
    ```

    Read files with extension `out`:

    ```
    for fn in get_files_from_range('flow_', ext='out'):
        print(fn) # `flow_00001.out`
                  # `flow_00002.out`
                  # ...
    ```

    Read a set of files with filenames `flow_00001.dat`, `flow_00002.dat`, ...,
    process them and write to files `out_00001.dat`, `out_00002.dat`, ...:

    ```
    for fn, fnout in get_files_from_range('flow_', output_base='out_'):
        print(fn, fnout) # `flow_00001.dat`, `out_00001.dat`
                         # `flow_00002.dat`, `out_00002.dat`
                         # ...
    ```

    Read files in sets of 2 and write to single file, sequentially:

    ```
    for fns, fnout in get_files_from_range('flow_', output_base='out_', num_per_output=2):
        print(fns, fnout) # [`flow_00001.dat`, `flow_00002.dat`], `out_00001.dat`
                          # [`flow_00003.dat`, `flow_00004.dat`], `out_00002.dat`
                          # ...
    ```

    Read files using two input bases:

    ```
    for fn1, fn2 in get_files_from_range('one_', 'two_'):
        print(fn1, fn2) # `one_00001.dat`, `two_00001.dat`
                        # `one_00002.dat`, `two_00002.dat`
                        # ...
    ```

    """

    def all_files_exist(filenames):
        if no_check:
            return True
        else:
            return all([os.path.exists(fn) for fn in filenames])

    def get_filename(base, i, ext):
        return "{}{:05d}.{}".format(base, i, ext)

    def get_yielded_single_or_list(filenames):
        if len(filenames) == 1:
            return filenames[0]
        else:
            return filenames

    def transpose_if_multiple_bases(groups, num_bases):
        if num_bases == 1:
            return groups
        else:
            transposed_groups = [[] for _ in range(num_bases)]

            for fns in groups:
                for i, fn in enumerate(fns):
                    transposed_groups[i].append(fn)

            return transposed_groups

    i = begin
    index_output = 1

    if num_per_output == None:
        num_per_output = 1

    if outext == None:
        outext = ext

    fns = [get_filename(base, i, ext) for base in fnbase]
    filename_group = []

    while (all_files_exist(fns) and (end == None or i <= end)):
        if num_per_output < 2:
            if output_base == None:
                yield get_yielded_single_or_list(fns)
            else:
                fnout = get_filename(output_base, i, outext)
                yield get_yielded_single_or_list(fns), fnout

        else:
            filename_group.append(get_yielded_single_or_list(fns))

            if len(filename_group) == num_per_output:
                fnout = get_filename(output_base, index_output, outext)
                yield transpose_if_multiple_bases(filename_group, len(fnbase)), fnout

                filename_group = []
                index_output += 1

        i += stride
        fns = [get_filename(base, i, ext) for base in fnbase]


def backup_file(path: str, log: TextIO | None = sys.stderr):
    """Backup a file that exists at the given path using the Gromacs standard.

    If a file at the given path exists it is enclosed to `#` and the lowest
    non-occupied index.

    By default a message about a performed backup is printed to `sys.stderr`.
    This can be turned off by supplying `log=None` or changed to another writer.

    # Arguments

    path (str): Path at which to look for already existing file to backup.

    log (fp): Writer to write a message into. Turn off by supplying `None` or `false`.

    # Examples

    Saving some data to a file that does not already exist:

    ```
    path = 'data.dat'
    backup_file(path) # Does nothing
    ```

    Saving some data to a file that exists:

    ```
    path = 'data.dat'
    backup_file(path) # Moves file at `data.dat` to `#data.dat.1#
    ```

    Saving some data to a file that already has a backup at `#data.dat.1#:

    ```
    path = 'data.dat'
    backup_file(path) # Moves file at `data.dat` to `#data.dat.2#
                      # Old backup is not moved: still at `#data.dat.1#`
    ```

    """

    def get_next(path, i):
        dirname = os.path.dirname(path)
        base = os.path.basename(path)

        return os.path.join(dirname, "#{}.{}#".format(base, i))

    if os.path.lexists(path):
        i = 1
        to_path = get_next(path, i)

        while os.path.lexists(to_path):
            i += 1
            to_path = get_next(path, i)

        if log:
            log.write("backed up '{}' to '{}'\n".format(path, to_path))

        os.rename(path, to_path)


# used only as a generic, but fixed, variable in the following function
Item = TypeVar('Item')


def loop_items(items: Iterable[Item],
               formatter: Callable[[Item], str] | None = None,
               fp: TextIO = stderr,
               quiet: bool = False,
               num_items_max: int = 500_000,
               ) -> Generator[Item, None, None]:
    r"""Loop through and yield items from a set, while printing information.

    This function is used to easily write CLI tools which work with sets
    of files, and it is useful to print how much of the work has been done.

    The printed information is each item's index in the set and total
    size of the set. By supplying a function with `formatter`, additional
    information about each item can be appended to the indexing.

    Each line is preceeded with a carriage return (`\r`), so that all items are
    printed into a single terminal line. After finishing the loop a newline
    (`\n`) is printed.

    By default information is printed into `stderr`. This can be changed
    by supplying another location with `fp`. The printing can be disabled
    with `quiet=True`.


    # Note

    * By default a maximum of `num_items_max` values are yielded. This is to
    avoid infinite memory allocations if, for example, an infinite iterator
    is given as input.


    # Examples

    ## Simple loop

    Print progress through a set (newlines added between
    each item for emphasis):

    ```
    items = ['one', 'two', 'three']
    for item in loop_items(items):
        # do something with each item
    ```

    Output (stderr):

    ```
    (1/3)
    (2/3)
    (3/3)
    # Newlines added between each item for emphasis.
    ```

    ## Formatting each item

    Also print the item as a regular string.

    ```
    items = ['one', 'two', 'three']
    for item in loop_items(items, formatter=str):
        # do something with each item
    ```

    Output (stderr):

    ```
    (1/3) one
    (2/3) two
    (3/3) three
    ```

    Or in uppercase (or whatever other function you can supply
    that takes the type of item, which can be anything, as an input).

    ```
    for item in loop_items(items, formatter=str.upper):
        # do something with each item
    ```

    Output (stderr):

    ```
    (1/3) ONE
    (2/3) TWO
    (3/3) THREE
    ```

    """

    items = list(itertools.islice(items, num_items_max))

    num_total = len(items)
    width = len(str(num_total))

    for i, item in enumerate(items):
        if not quiet:
            fp.write(f"\r({i + 1:{width}}/{num_total}) ")

            if formatter != None:
                fp.write(f"{formatter(item)} ")

        yield item

    if not quiet:
        fp.write("\n")

    return None
