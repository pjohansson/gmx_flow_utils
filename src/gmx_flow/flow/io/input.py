import gzip
import numpy as np
import os
import warnings

from collections.abc import Sequence

from ..gmxflow import GmxFlow, GmxFlowVersion

# Fields expected to be read in the files.
__FIELDS = ['X', 'Y', 'N', 'T', 'M', 'U', 'V']

# Fields which represent data in the flow field, excluding positions.
__DATA_FIELDS = ['N', 'T', 'M', 'U', 'V']

# List of fields in the order of writing.
__FIELDS_ORDERED = ['N', 'T', 'M', 'U', 'V']


def read_flow(filename: str) -> GmxFlow:
    """Read flow field data from a file.

    Args:
        filename (str): File to read data from.

    Returns:
        GmxFlow: Flow field data.

    """

    def get_header_field(info, label):
        try:
            field = info[label]
        except KeyError:
            raise ValueError(f"could not read {label} from `{filename}`")

        return field

    data, info = _read_data(filename)

    shape = get_header_field(info, 'shape')
    spacing = get_header_field(info, 'spacing')
    origin = get_header_field(info, 'origin')
    version_str = get_header_field(info, 'format')

    if version_str == 'GMX_FLOW_1':
        version = GmxFlowVersion(1)
    elif version_str == 'GMX_FLOW_2':
        version = GmxFlowVersion(2)
    else:
        raise ValueError(f"unknown file format `{version_str}`")

    dtype = [(l, float) for l in data.keys()]
    num_bins = np.prod(shape)
    data_new = np.zeros((num_bins, ), dtype=dtype)

    for key, value in data.items():
        data_new[key] = value

    return GmxFlow(
        data=data_new,
        shape=shape,
        spacing=spacing,
        version=version,
        origin=origin,
    )


def _read_data(filename: str) -> tuple[dict[str, np.ndarray], dict[str, str]]:
    """Read field data from a file.

    The data is returned on a regular grid, adding zeros for bins with no values
    or which are not present in the (possibly not-full) input grid.

    The `x` and `y` coordinates are bin center positions, not corner.

    If the given filename has the extension '.gz' the file is assumed
    to be compressed with gzip. It will be decompressed before reading.

    Args:
        filename (str): A file to read data from.

    Returns:
        (dict, dict): 2-tuple of dict's with data and information.

    """

    def read_file(filename: str, mode: str) -> bytes:
        _, ext = os.path.splitext(filename)
        assume_gzip = ext == '.gz'

        if assume_gzip:
            fp = gzip.open(filename, mode)
        else:
            fp = open(filename, mode)

        try:
            content = fp.read()
        except gzip.BadGzipFile:
            warnings.warn(
                f"Tried to read `{filename}` as a gzip file "
                "due to its extension, but it did not work: "
                "reading it as a non-gzipped file instead"
            )

            fp = open(filename, mode)
            content = fp.read()

        fp.close()

        return content

    def split_file_into_header_and_data(
            content: bytes,
            sep: bytes = b'\0',
    ) -> tuple[bytes, bytes]:
        header, _, data = content.partition(sep)

        return header, data

    content = read_file(filename, 'rb')
    header_bytes, data_bytes = split_file_into_header_and_data(content)

    fields, num_values, info = _read_header(header_bytes)
    data = _read_values(data_bytes, num_values, fields)

    x0, y0 = info['origin']
    nx, ny = info['shape']
    dx, dy = info['spacing']

    x = x0 + dx * (np.arange(nx) + 0.5)
    y = y0 + dy * (np.arange(ny) + 0.5)
    xs, ys = np.meshgrid(x, y, indexing='ij')

    grid = np.zeros((nx, ny), dtype=[(l, float) for l in __FIELDS])
    grid['X'] = xs
    grid['Y'] = ys

    for l in __DATA_FIELDS:
        grid[l][data['IX'], data['IY']] = data[l]

    grid = grid.ravel()

    return {l: grid[l] for l in __FIELDS}, info


def _read_values(content: bytes,
                 num_values: int,
                 fields: Sequence[str],
                 ) -> dict[str, np.ndarray]:
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

    offset = 0
    data = {}

    for label in fields:
        dtype = dtypes[label]

        data[label] = np.frombuffer(
            content,
            count=num_values,
            offset=offset,
            dtype=dtype,
        )

        offset += num_values * np.dtype(dtype).itemsize

    return data


def _read_header(content: bytes) -> tuple[list[str], int, dict[str, str]]:
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

    info = {}
    header_str = content.decode('ascii')

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
