"""File parsing and backup utilities."""

import os
import sys

def get_files_from_range(
    fnbase, 
    output_base=None, num_per_output=None, 
    begin=1, end=None, ext='dat'):
    """Yield paths to existing files with a given base path.

    Filenames are constructed using the format `{base}{:05d}.{ext}`,
    i.e. `flow_00001.dat`, `flow_00002.dat`, ... 

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

    fnbase (str): Given filename base to find and yield files for.

    output_base (str): Given filename base to yield output files for.

    num_per_output (int): Yield this many input files at ones for a single output file.

    begin (int): First index to yield input files for.

    end (int): Last index to yield input files for.

    ext (str): Extension to yield files for.


    # Yields

    fn (str):             input files 
    fn, fnout (str, str): input and output files if `output_base` != `None`
    fns, fnout ([str], str): list of input files for a single output file
                             if `output_base` and `num_per_output` != `None`

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

    """

    def get_filename(base, i):
        return "{}{:05d}.{}".format(base, i, ext)

    i = begin
    index_output = 1

    fn = get_filename(fnbase, i)
    filename_group = []

    while os.path.exists(fn) and (end == None or i <= end):
        if num_per_output == None:
            if output_base == None:
                yield fn
            else:
                fnout = get_filename(output_base, i)
                yield fn, fnout
        
        else:
            filename_group.append(fn)

            if len(filename_group) == num_per_output:
                fnout = get_filename(output_base, index_output)
                yield filename_group, fnout

                filename_group = []
                index_output += 1

        i += 1
        fn = get_filename(fnbase, i)


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


