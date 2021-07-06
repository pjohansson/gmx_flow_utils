import numpy as np

# Fields expected to be read in the files.
_FIELDS = ['X', 'Y', 'N', 'T', 'M', 'U', 'V']

# Fields which represent data in the flow field, excluding positions.
_DATA_FIELDS = ['N', 'T', 'M', 'U', 'V']

# List of fields in the order of writing.
_FIELDS_ORDERED = ['N', 'T', 'M', 'U', 'V']


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

