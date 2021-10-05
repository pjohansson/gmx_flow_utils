import copy
import numpy as np

# Fields expected to be read in the files.
_FIELDS = ['X', 'Y', 'N', 'T', 'M', 'U', 'V']

# Fields which represent data in the flow field, excluding positions.
_DATA_FIELDS = ['N', 'T', 'M', 'U', 'V']

# List of fields in the order of writing.
_FIELDS_ORDERED = ['N', 'T', 'M', 'U', 'V']


def read_data(filename):
    """Read field data from a file.

    The data is returned on a regular grid, adding zeros for bins with no values
    or which are not present in the (possibly not-full) input grid.

    The `x` and `y` coordinates are bin center positions, not corner.

    Args:
        filename (str): A file to read data from.

    Returns:
        (dict, dict): 2-tuple of dict's with data and information.

    """

    with open(filename, 'rb') as fp:
        fields, num_values, info = _read_header(fp)
        data = _read_values(fp, num_values, fields)

    x0, y0 = info['origin']
    nx, ny = info['shape']
    dx, dy = info['spacing']

    x = x0 + dx * (np.arange(nx) + 0.5)
    y = y0 + dy * (np.arange(ny) + 0.5)
    xs, ys = np.meshgrid(x, y, indexing='ij')

    grid = np.zeros((nx, ny), dtype=[(l, float) for l in _FIELDS])
    grid['X'] = xs
    grid['Y'] = ys

    for l in _DATA_FIELDS:
        grid[l][data['IX'], data['IY']] = data[l]

    grid = grid.ravel()

    return {l: grid[l] for l in _FIELDS}, info


def _read_values(fp, num_values, fields):
    """Read the binary data in the given order."""

    dtypes = {
        'IX': np.uint64,
        'IY': np.uint64,
        'N': np.float32,
        'T': np.float32,
        'M': np.float32,
        'U': np.float32,
        'V': np.float32,
    }

    return {
        l: np.fromfile(fp, dtype=dtypes[l], count=num_values)
        for l in fields
    }


def _read_header(fp):
    """Read header information and forward the pointer to the data."""

    def read_shape(line):
        return tuple(int(v) for v in line.split()[1:3])

    def read_spacing(line):
        return tuple(float(v) for v in line.split()[1:3])

    def read_num_values(line):
        return int(line.split()[1].strip())

    def read_format(line):
        return line.lstrip("FORMAT").strip()

    def parse_field_labels(line):
        return line.split()[1:]

    def read_header_string(fp):
        buf_size = 1024
        header_str = ""

        while True:
            buf = fp.read(buf_size)

            pos = buf.find(b'\0')

            if pos != -1:
                header_str += buf[:pos].decode("ascii")
                offset = buf_size - pos - 1
                fp.seek(-offset, 1)
                break
            else:
                header_str += buf.decode("ascii")

        return header_str

    info = {}
    header_str = read_header_string(fp)

    for line in header_str.splitlines():
        line_type = line.split(maxsplit=1)[0].upper()

        if line_type == "SHAPE":
            info['shape'] = read_shape(line)
        elif line_type == "SPACING":
            info['spacing'] = read_spacing(line)
        elif line_type == "ORIGIN":
            info['origin'] = read_spacing(line)
        elif line_type == "FIELDS":
            fields = parse_field_labels(line)
        elif line_type == "NUMDATA":
            num_values = read_num_values(line)
        elif line_type == "FORMAT":
            info['format'] = read_format(line)

    info['num_bins'] = info['shape'][0] * info['shape'][1]

    return fields, num_values, info

