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

    grid = np.zeros((nx, ny), dtype=[(l, np.float) for l in _FIELDS])
    grid['X'] = xs
    grid['Y'] = ys

    for l in _DATA_FIELDS:
        grid[l][data['IX'], data['IY']] = data[l]

    grid = grid.ravel()

    return {l: grid[l] for l in _FIELDS}, info


def write_data(path, data, info, check_label='M'):
    """Write data to disk in a data format with only non-empty bins.

    Args:
        path (str): Write to a file at this path.

        data (dict): Data to write.

        info (dict): Information about the data. Must contain values for 
            `shape`, `spacing` and `origin`, each a 2-tuple of floats.

    Keyword args:
        check_label (str): Label in dict which must be non-zero for a bin to be written.
            Set to `None` to write all bins.

    """

    nx, ny = info['shape']

    if check_label != None:
        inds = data[check_label] != 0.
    else:
        inds = [True for _ in data[_FIELDS_ORDERED[0]]]

    num_elements = np.count_nonzero(inds)

    ix = np.arange(nx, dtype=np.uint64)
    iy = np.arange(ny, dtype=np.uint64)
    ixs, iys = np.meshgrid(ix, iy, indexing='ij')

    output_data = [
            ixs.ravel()[inds],
            iys.ravel()[inds]
        ] + [np.array(data[l][inds], dtype=np.float32) for l in _FIELDS_ORDERED]

    file_format = info.get('format', 'GMX_FLOW_1')

    with open(path, "wb") as fp:
        _write_header(
            fp, info['shape'], info['spacing'], info['origin'], file_format, num_elements
        )

        for vs in output_data:
            vs.tofile(fp)


def average_data(data_list):
    """Average a given list of flow fields.

    The flow fields must be of identical shape and be regular. It is further
    assumed that they have the same origin and bin spacing, and that the bins 
    have the same index ordering. The `read_data` function reads the data in
    such a format and is compatible with this function.

    If the input list is empty, `None` is returned.

    """

    try:
        data = copy.deepcopy(data_list[0])
    except IndexError:
        return None

    for d in data_list[1:]:
        data['M'] += d['M']
        data['N'] += d['N']

        # Averaging the actual temperature properly requires access to the number 
        # of degrees of freedom for atoms in the bin, which we do not have. We 
        # thus simply take the arithmetic mean.
        data['T'] += d['T']

        # Velocities are mass-averaged.
        data['U'] += d['M'] * d['U']
        data['V'] += d['M'] * d['V']

    num_data = float(len(data_list))

    # We do not want to divide the velocities with 0. Thus we set the mass in these 
    # bins to a number. Since no data is present in the bins, the velocities will be 0
    # after the division.
    mass_div = copy.deepcopy(data['M'])
    mass_div[mass_div == 0.] = num_data

    data['U'] /= mass_div
    data['V'] /= mass_div

    data['M'] /= num_data
    data['N'] /= num_data
    data['T'] /= num_data

    return data


def convert_gmx_flow_1_to_2(data, info, width):
    """Convert flow data from 'GMX_FLOW_1' to 'GMX_FLOW_2'.

    This changes the field 'M' to represent the mass density instead of 
    the total mass in the bin. Thus we also require the width of the system,
    in order to calculate the bin volume.

    If the `format` field in `info` is already 'GMX_FLOW_2' an unmodified 
    copy of the original data is returned.

    """

    info = copy.deepcopy(info)
    data = copy.deepcopy(data)

    if info['format'] == 'GMX_FLOW_1':
        (dx, dy) = info['spacing']
        volume = dx * dy * width

        if 'M' in data:
            data['M'] /= volume

        info['format'] = 'GMX_FLOW_2'

    return data, info


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


def _write_header(fp, shape, spacing, origin, file_format, num_elements):
    def floats_to_string(label, values):
        return ' '.join([label] + ["{:12f}".format(v) for v in values]) + '\n'

    def ints_to_string(label, values):
        return ' '.join([label] + ["{}".format(v) for v in values]) + '\n'

    fp.write("FORMAT {}\n".format(file_format).encode())

    fp.write(floats_to_string("ORIGIN", origin).encode())
    fp.write(ints_to_string("SHAPE", shape).encode())
    fp.write(floats_to_string("SPACING", spacing).encode())

    fp.write("NUMDATA {}\n".format(num_elements).encode())

    fp.write("FIELDS IX IY".encode())
    for l in _FIELDS_ORDERED:
        fp.write(" {}".format(l).encode())
    fp.write("\n".encode())

    mass_comment = "COMMENT 'M' is the average mass{}\n".format(
            " density" if file_format == "GMX_FLOW_2" else "")    

    fp.write("COMMENT Grid is regular but only non-empty bins are output\n".encode())
    fp.write("COMMENT There are 'NUMDATA' non-empty bins and that many values are stored for each field\n".encode())
    fp.write("COMMENT 'FIELDS' is the different fields for each bin:\n".encode())
    fp.write("COMMENT 'IX' and 'IY' are bin indices along x and y respectively\n".encode())
    fp.write("COMMENT 'N' is the average number of atoms\n".encode())
    #fp.write("COMMENT 'M' is the average mass\n".encode())
    fp.write(mass_comment.encode())
    fp.write("COMMENT 'T' is the temperature\n".encode())
    fp.write("COMMENT 'U' and 'V' is the mass-averaged flow along x and y respectively\n".encode())
    fp.write("COMMENT Data is stored as 'NUMDATA' counts for each field in 'FIELDS', in order\n".encode())
    fp.write("COMMENT 'IX' and 'IY' are 64-bit unsigned integers\n".encode())
    fp.write("COMMENT Other fields are 32-bit floating point numbers\n".encode())
    fp.write("COMMENT Example: with 'NUMDATA' = 4 and 'FIELDS' = 'IX IY N T', "
             "the data following the '\\0' marker is 4 + 4 64-bit integers "
             "and then 4 + 4 32-bit floating point numbers\n".encode())

    fp.write(b"\0")

