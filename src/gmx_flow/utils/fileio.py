"""File parsing and backup utilities."""

import os
import sys

def get_files_from_range(fnbase, fnoutbase, num=None, begin=1, end=None, extension='dat'):
    """Yield files from a range along with the output destination.

    Filenames are constructed using the format `{base}{:05d}.{ext}`,
    i.e. `flow_00001.dat`, `flow_00002.dat`, ... 

    Unless specific beginning and end points are specified, the function 
    yields all filenames with the given base and numbering starting from
    index 1 until a file with the next larger index is not found.

    # Arguments

    fnbase (str): Given filename base to find and yield files for.

    fnoutbase (str): Given filename base to yield output files for.

    num (int): Yield this many input files at ones, for a single output file.

    begin (int): First index to yield input files for.

    end (int): Last index to yield input files for.

    extension (str): Extension to yield files for.

    # Returns

    fn, fnout (str, str): input and output files 
    [fns], fnout (list(str), str): (if num != None) list of input files and a single output

    # Examples

    Read a set of files with filenames `flow_00001.dat`, `flow_00002.dat`, ...,
    process them and write to files `out_00001.dat`, `out_00002.dat`, ...:

    ```
    for fn, fnout in get_files_from_range('flow_', 'out_'):
        print(fn, fnout) # `flow_00001.dat`, `out_00001.dat`
                         # `flow_00002.dat`, `out_00002.dat`
                         # ...
    ```

    Read files in a range of indices 5 to 10 (inclusive):

    ```
    for fn, fnout in get_files_from_range('flow_', 'out_', begin=5, end=10):
        print(fn, fnout) # `flow_00005.dat`, `out_00005.dat`
                         # `flow_00006.dat`, `out_00006.dat`
                         # ...
                         # `flow_00010.dat`, `out_00010.dat`
    ```

    Read files in sets of 2 and write to single file, sequentially:

    ```
    for fn, fnout in get_files_from_range('flow_', 'out_', num=2):
        print(fn, fnout) # [`flow_00001.dat`, `flow_00002.dat`], `out_00001.dat`
                         # [`flow_00003.dat`, `flow_00004.dat`], `out_00002.dat`
                         # ...
    ```

    Read and write files with extension `out`:

    ```
    for fn, fnout in get_files_from_range('flow_', 'out_', extension='out'):
        print(fn, fnout) # `flow_00001.out`, `out_00001.out`
                         # `flow_00002.out`, `out_00002.out`
                         # ...
    ```

    """

    def get_filename(base, i):
        return "{}{:05d}.{}".format(base, i, extension)

    i = begin
    n = 1
    fn = get_filename(fnbase, i)

    filenames = []

    while os.path.exists(fn) and (end == None or i <= end):
        filenames.append(fn)

        if num != None and len(filenames) == num:
            yield filenames, get_filename(fnoutbase, n)

            n += 1
            filenames = []

        i += 1
        fn = get_filename(fnbase, i)

    if num == None and filenames != []:
        yield filenames, get_output(n)


def backup_file(path, log=sys.stderr):
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


