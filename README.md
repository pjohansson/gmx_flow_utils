# Gromacs Flow Field Utilities

A collection of Python modules and scripts for working with flow field
datafiles written a Gromacs fork for flow field collection
(https://github.com/pjohansson/gromacs-flow-field).


## Installation

Clone or download the directory and install with `pip`. Note that this
is a Python 3 package. Some modern features (e.g. typing) is used
which may require an up-to-date version of Python 3.

```bash
git clone https://github.com/pjohansson/gmx_flow_utils.git
cd gmx_flow_utils/

# Install dependencies
pip install -r requirements.txt

# Install package
pip install .
```


## Examples

The main module of the package is `gmx_flow` which contains functions
for reading and writing flow field data.

### Reading data

Example files are in the `include` directory.

```python
from gmx_flow import read_flow

flow = read_flow('include/flow_00001.dat')

# Accessing the flow field data inside bins:
xs = flow.data['X']      # bin positions along x
ys = flow.data['Y']      # bin positions along y
us = flow.data['U']      # flow along x
vs = flow.data['V']      # flow along y
flow = flow.data['flow'] # flow magnitude: np.sqrt(us**2 + vs**2)
ms = flow.data['M']      # mass (density)
ns = flow.data['N']      # number of atoms
ts = flow.data['T']      # temperature (only for SPC/E)

# Short accessors for common data:
assert np.array_equal(flow.x, flow.data['X'])
assert np.array_equal(flow.y, flow.data['Y'])
assert np.array_equal(flow.u, flow.data['U'])
assert np.array_equal(flow.v, flow.data['V'])
assert np.array_equal(flow.mass, flow.data['M'])
assert np.array_equal(flow.flow, flow.data['flow'])

# Accessing metadata:
assert flow.shape == (80, 164)           # 80 bins along x and 164 along y
assert flow.spacing == (0.25, 0.255128)  # bin spacing (size) along x and y
assert np.isclose(flow.box_size, (20., 41.840992)) # size of box
```

### Using data
```python
from gmx_flow import read_flow

flow = read_flow('include/flow_00001.dat')

# Bin indexing of `data` is [x, y]:
lowest_row = flow.data[:, 0]
leftmost_column = flow.data[0, :]

# Third bin along x, fifth along y:
bin_3_5 = flow.data[3, 5]

```

### Writing data

```python
from gmx_flow import read_flow, write_flow

flow = read_flow('include/flow_00001.dat')

# Modify data
flow.data['U'] *= 0.5
# ...

# Write the new data to disk
write_flow('out_00001.dat', flow)
```


## Scripts

The package comes with some scripts which will be installed alongside
the `gmx_flow` module.

### `average_flow_fields.py`

Script for averaging flow fields. See its help for more information:

### `convert_gmx_flow_1_to_2.py`

Script for converting the flow field map format from version `GMX_FLOW_1`
to `GMX_FLOW_2`. The latter contains the bin mass density instead of the
total bin mass from the simulations, a full on improvement.

### `draw_flow_map.py`

Script which draws 2D height maps of a flow field. Can be used to visualize
the mass (density) or another quantity through the system.

### `draw_flow_field.py`

Script which draws quiver plots of the flow inside a flow field. Arrows
can be colored with mass or other quantities.


## Utilities
Some additional utility functions are available in the `gmx_flow.utils`
module. These are created to simplify the creation of CLI-tools, such as
the included scripts.


## License

All tools and modules are distributed under the permissive Blue Oak license.
See [`LICENSE.md`](LICENSE.md) for more information.
