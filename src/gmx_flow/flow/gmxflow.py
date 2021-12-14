import numpy as np

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from copy import deepcopy
from enum import Enum, auto


class GmxFlowVersion(Enum):
    """Version of flow field data file.

    Could possibly be an int, but using it as an enum means we
    are limiting possible values to a known set.

    """

    GMX_FLOW_1 = auto()
    GMX_FLOW_2 = auto()

    def as_header(self):
        if self == GmxFlowVersion(1):
            return 'GMX_FLOW_1'
        else:
            return 'GMX_FLOW_2'


@dataclass
class GmxFlow:
    """Class for a `GMX_FLOW` object containing flow field data.

    The flow field data is accessed through the `data` accessor.
    This is a numpy record where all the indices correspond to
    a bin on the grid. To access specific fields (or quantities)
    from the grid or a bin, supply the field label.

    After initialization the data record has been set to the input
    `shape == (nx, ny)` tuple.

    # Examples

    ## Accessing grid positions and data

    ```
    x = flow.data['X'] # bin positions along x
    y = flow.data['Y'] #                 ... y
    m = flow.data['M'] # mass density in those same bins

    # Axis 0 is along x, axis 1 along y
    ix = 5
    iy = 8
    bin = flow.data[ix, iy]
    ```

    ## Additional accessors for common fields

    Some common fields can be accessed directly.

    ```
    assert np.array_equal(flow.x, flow['data']['X'])
    assert np.array_equal(flow.y, flow['data']['Y'])
    assert np.array_equal(flow.u, flow['data']['U'])
    assert np.array_equal(flow.v, flow['data']['V'])
    assert np.array_equal(flow.mass, flow['data']['M'])
    ```

    ## Construction

    This is a non-standard example where the grid contains bin
    positions, flow and and a mass density. Flow fields created
    by the Gromacs code typically contain additional quantities
    like flow velocity, but this class does not by itself require
    those to be present.

    ```
    import numpy as np

    nx = 10
    ny = 5

    dx = 1.0
    dy = 2.0

    x = dx * np.arange(nx)
    y = dy * np.arange(ny)
    xs, ys = np.meshgrid(x, y, indexing='ij')

    dtype = [(label, float) for label in ['X', 'Y', 'U', 'V', 'M']]
    data = np.zeros((nx, ny), dtype=dtype)

    data['X'] = xs
    data['Y'] = ys
    data['U'] = np.random.random(data.shape)
    data['V'] = np.random.random(data.shape)
    data['M'] = np.random.random(data.shape)

    flow = GmxFlow(data, shape=(nx, ny), spacing=(dx, dy))
    ```

    """

    data: np.ndarray = field(repr=False)
    "View of data for bins in the flow field: a numpy record with labels in `fields`"

    shape: Tuple[int, int]
    "Number of bins along each axis in the grid"

    spacing: Tuple[float, float]
    "Spacing between bins in grid"

    box_size: Tuple[float, float] = field(init=False)
    "Total size of box"

    units: Dict[str, str] = field(init=False, repr=False)
    "Dictionary with physical units of each field"

    descriptions: Dict[str, str] = field(init=False, repr=False)
    "Dictionary with a description of each field"

    fields: List[str] = field(init=False)
    "List of all fields for the `data` record"

    version: GmxFlowVersion = GmxFlowVersion(2)
    "Version of flow field data format"

    origin: Tuple[float, float] = (0., 0.)
    "Lower-left corner position of bin (0, 0)"

    # Field accessors
    x: np.ndarray = field(default=None, repr=False)
    "Center positions of each bin along the `x` axis"

    y: np.ndarray = field(default=None, repr=False)
    "Center positions of each bin along the `y` axis"

    u: np.ndarray = field(default=None, repr=False)
    "Mass flow of each bin along the `x` axis"

    v: np.ndarray = field(default=None, repr=False)
    "Mass flow of each bin along the `y` axis"

    flow: np.ndarray = field(default=None, repr=False)
    "Flow magnitude in each bin (sqrt(u**2 + v**2))"

    mass: np.ndarray = field(default=None, repr=False)
    "Mass density (or total mass for `GMX_FLOW_1`) of each bin"

    # Background data and consts
    _backup_data: np.ndarray = field(init=False, repr=False)
    "Stored copy of the original data, used to restore `data` if needed"

    _xlabel: str = field(default='X', repr=False)
    _ylabel: str = field(default='Y', repr=False)
    _x_flow_label: str = field(default='U', repr=False)
    _y_flow_label: str = field(default='V', repr=False)
    _mass_label: str = field(default='M', repr=False)
    _flow_label: str = field(default='flow', repr=False)

    def __post_init__(self):
        try:
            self._backup_data = self.data.copy().reshape(self.shape)
        except ValueError:
            raise ValueError(
                f"cannot reshape data array with shape {self.data.shape} "
                f"into input shape {self.shape}")

        self._add_flow_magnitude()
        self.reset_view()

        self.fields = list(self.data.dtype.names)
        self.units = _get_units_dict(self.version)
        self.descriptions = _get_descriptions_dict(self.version)

    def set_xlim(self, xmin: Optional[float], xmax: Optional[float]):
        """Set limits on bins along the x axis."""

        self.set_clim(xmin, xmax, self._xlabel)
        self._update_shape()

    def set_ylim(self, ymin: Optional[float], ymax: Optional[float]):
        """Set limits on bins along the y axis."""

        self.set_clim(ymin, ymax, self._ylabel)
        self._update_shape()

    def set_clim(self, cmin: Optional[float], cmax: Optional[float], label: str):
        """Set limits on shown bins for any cutoff label.

        Note that this removes bins from the data. Thus we are no longer
        guaranteed to have a rectilinear grid and the `shape` of the
        grid will be 1D by necessity. Bin positions are still accessed
        through the `X` and `Y` fields respectively.

        """

        if cmin == None:
            cmin = -np.inf

        if cmax == None:
            cmax = np.inf

        mask = (self.data[label] >= cmin) & (self.data[label] <= cmax)
        self.data = self.data[mask]
        self._update_shape()

    def copy(self) -> 'GmxFlow':
        """Return a deep copy of the object."""

        flow_copy = deepcopy(self)
        flow_copy.reset_view()

        return flow_copy

    def reset_view(self):
        """Reset `data` to original view."""

        self.data = self._backup_data[:, :]
        self.shape = self._backup_data.shape
        self._update_field_accessors()
        self._update_box_size()

    def _add_flow_magnitude(self):
        """Add `flow = sqrt(U**2 + V**2) to `_backup_data`, etc."""

        try:
            us = self._backup_data[self._x_flow_label]
            vs = self._backup_data[self._y_flow_label]
            magnitude = np.sqrt(us**2 + vs**2)
        except:
            pass
        else:
            current_fields = list(self._backup_data.dtype.names)

            dtype = [(l, float) for l in current_fields + [self._flow_label]]
            updated_data = np.zeros(self._backup_data.shape, dtype=dtype)

            for label in current_fields:
                updated_data[label] = self._backup_data[label]

            updated_data[self._flow_label] = magnitude

            self._backup_data = updated_data

    def _update_box_size(self):
        """Update the box size of the current `data` grid."""

        dx, dy = self.spacing
        nx, ny = self.shape

        self.box_size = dx * float(nx), dy * float(ny)

    def _update_field_accessors(self):
        """Update the views of each field accessor to the `data` object.

        This must be called if the view into `data` is modified. For example
        if data is updated with a slice view, these accessors should point
        to that same slice.

        """

        self.x = self.data[self._xlabel]
        self.y = self.data[self._ylabel]

        try:
            self.u = self.data[self._x_flow_label]
            self.v = self.data[self._y_flow_label]
        except:
            pass

        try:
            self.mass = self.data[self._mass_label]
        except:
            pass

        try:
            self.flow = self.data[self._flow_label]
        except:
            pass

    def _update_shape(self):
        """Calculate the shape of the current `data` and update all shapes.

        If the grid is still regular the shape will be applied to the `data`
        array.

        """

        self.shape = _calc_shape_from_data(
            self.data[self._xlabel],
            self.data[self._ylabel],
            self.spacing)

        if self.data.size == np.prod(self.shape):
            self.data = np.resize(self.data, self.shape)

        self._update_field_accessors()
        self._update_box_size()


def _get_descriptions_dict(version: GmxFlowVersion) -> Dict[str, str]:
    mass = 'Mass density' if version == GmxFlowVersion(2) else 'Total mass'

    return {
        'X': 'Axis',
        'Y': 'Axis',
        'U': 'Velocity',
        'V': 'Velocity',
        'flow': 'Flow magnitude',
        'M': mass,
        'T': 'Temperature',
        'N': 'Number of atoms',
    }


def _get_units_dict(version: GmxFlowVersion) -> Dict[str, str]:
    mass = 'u/nm^3' if version == GmxFlowVersion(2) else 'u'

    return {
        'X': 'nm',
        'Y': 'nm',
        'U': 'nm/ps',
        'V': 'nm/ps',
        'flow': 'nm/ps',
        'M': mass,
        'T': 'K',
        'N': '',
    }


def _calc_shape_from_data(
    xs: np.ndarray,
    ys: np.ndarray,
    spacing: Tuple[float, float],
) -> Tuple[int, int]:
    """Calculate (nx, ny) from the min/max bin positions and spacing."""

    def calc_along_axis(values, diff):
        vmin = values.min()
        vmax = values.max()

        return int(np.round((vmax - vmin) / diff)) + 1

    dx, dy = spacing
    nx = calc_along_axis(xs, dx)
    ny = calc_along_axis(ys, dy)

    return nx, ny
