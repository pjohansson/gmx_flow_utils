import numpy as np
from typing import BinaryIO

from .utils import open_file_maybe_gzip
from ..gmxflow import GmxFlow

# Fields expected to be read in the files.
__FIELDS = ['X', 'Y', 'N', 'T', 'M', 'U', 'V']

# Fields which represent data in the flow field, excluding positions.
__DATA_FIELDS = ['N', 'T', 'M', 'U', 'V']

# List of fields in the order of writing.
__FIELDS_ORDERED = ['N', 'T', 'M', 'U', 'V']


def write_flow(path: str, flow: GmxFlow):
    """Write flow field to disk at the given path.

    # Notes
    The flow field requires the following fields: [X, Y, U, V, M, N, T]

    Additional fields outside of the list will not be saved.

    # Exceptions
        ValueError: If the flow field does not contain all required fields.

    """

    missing_fields = set(__FIELDS) - set(flow.fields)

    if len(missing_fields) > 0:
        raise ValueError(
            f"flow field missing required fields `({missing_fields})`")

    data = flow.data.ravel()

    # Remove empty bins from the output by checking the mass field,
    # else keep all the indices
    # TODO: Add boolean option and tests for this
    if True:
        keep_inds = data['M'] != 0.
    else:
        keep_inds = [True for _ in flow.data[__FIELDS_ORDERED[0]]]

    num_bins, packed_data = pack_data(data, flow.shape, keep_inds)

    with open_file_maybe_gzip(path, mode='wb') as fp:
        _write_header(
            fp,
            flow.shape,
            flow.spacing,
            flow.origin,
            flow.version.as_header(),
            num_bins,
        )

        for vs in packed_data:
            fp.write(vs.tobytes())


def pack_data(data: np.ndarray,
              shape: tuple[int, int],
              keep_inds: np.ndarray,
              ) -> tuple[int, list[np.ndarray]]:
    nx, ny = shape
    num_bins = np.count_nonzero(keep_inds)

    ix = np.arange(nx, dtype=np.uint64)
    iy = np.arange(ny, dtype=np.uint64)
    ixs, iys = np.meshgrid(ix, iy, indexing='ij')

    # Create the list first with the bin indices, then with
    # the data fields in a set order
    packed_data = [
        ixs.ravel()[keep_inds],
        iys.ravel()[keep_inds]
    ] + [
        np.array(data[l][keep_inds], dtype=np.float32)
        for l in __FIELDS_ORDERED
    ]

    return num_bins, packed_data


def _write_header(fp: BinaryIO,
                  shape: tuple[int, int],
                  spacing: tuple[float, float],
                  origin: tuple[float, float],
                  file_format: str,
                  num_elements: int,
                  ):
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
    for l in __FIELDS_ORDERED:
        fp.write(" {}".format(l).encode())
    fp.write("\n".encode())

    mass_comment = "COMMENT 'M' is the average mass{}\n".format(
        " density" if file_format == "GMX_FLOW_2" else "")

    fp.write("COMMENT Grid is regular but only non-empty bins are output\n".encode())
    fp.write("COMMENT There are 'NUMDATA' non-empty bins and that many values are stored for each field\n".encode())
    fp.write("COMMENT 'FIELDS' is the different fields for each bin:\n".encode())
    fp.write(
        "COMMENT 'IX' and 'IY' are bin indices along x and y respectively\n".encode())
    fp.write("COMMENT 'N' is the average number of atoms\n".encode())
    fp.write(mass_comment.encode())
    fp.write("COMMENT 'T' is the temperature\n".encode())
    fp.write(
        "COMMENT 'U' and 'V' is the mass-averaged flow along x and y respectively\n".encode())
    fp.write("COMMENT Data is stored as 'NUMDATA' counts for each field in 'FIELDS', in order\n".encode())
    fp.write("COMMENT 'IX' and 'IY' are 64-bit unsigned integers\n".encode())
    fp.write("COMMENT Other fields are 32-bit floating point numbers\n".encode())
    fp.write("COMMENT Example: with 'NUMDATA' = 4 and 'FIELDS' = 'IX IY N T', "
             "the data following the '\\0' marker is 4 + 4 64-bit integers "
             "and then 4 + 4 32-bit floating point numbers\n".encode())

    fp.write(b"\0")
