# Gromacs Flow Field Utilities

A collection of modules and scripts for working with flow field 
datafiles written a Gromacs fork for flow field collection 
(https://github.com/pjohansson/gromacs-flow-field).

## `gmx_flow.py`

Functions for reading and writing data. Its public functions are documented.

The Python scripts require access to this module.

### Examples

Reading data (example files in `include` directory):

```python
from gmx_flow import read_data

data, info = read_data('include/flow_00001.dat')

# `info` contains metadata about the grid
assert info['shape'] == (80, 164)          # 80 bins along x and 164 along y
assert info['spacing'] == (0.25, 0.255128) # bin spacing (i.e. bin size) along x and y 
assert info['origin'] == (0.0, 0.0)        # origin of bottom-left corner of grid
assert info['num_bins'] == 80 * 164        # total number of bins in grid

# `data` is a dict with fields which are `numpy` arrays of data in bins
data['X'], data['Y'] # x and y positions of bins
data['M']            # average mass in bin
data['N']            # average number of atoms in bin
data['T']            # average temperature in bin
data['U'], data['V'] # mass-averaged velocity along x and y in bin

# All arrays are of equal shape and the data is laid out in x-major, y-minor order
assert data['X'].size == info['num_bins']
assert (data['X'][:164] == 0.125).all()    # first column of 160 bins along y
assert (data['X'][164:328] == 0.375).all() # second column
                                           # etc.
```

Writing data:

```python
from gmx_flow import write_data

data, info = read_data('include/flow_00001.dat')

# Modify data and possibly info
data['U'] *= 0.5
# ...

# Write the new data to disk
write_data('out_00001.dat', data, info)
```

## `average_flow_fields.py`

Script for averaging flow fields. See its help for more information:

`$ python3 average_flow_fields.py -h`

## Todo

Create a proper class for flow fields, instead of exposing separate 
data and info dicts.

## License

All tools and modules are distributed under the permissive Blue Oak license. 
See [`LICENSE.md`](LICENSE.md) for more information.
