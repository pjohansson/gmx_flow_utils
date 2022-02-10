import numpy as np
import os

import gmx_flow
from gmx_flow.flow.io.input import _read_data

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_files',
)


def test_read_gmx_flow_is_consistent_with_read_data():
    filename = os.path.join(FIXTURE_DIR, 'flow_field0.dat')

    flow = gmx_flow.read_flow(filename)
    data, info = _read_data(filename)

    assert flow.shape == info['shape']
    assert flow.spacing == info['spacing']
    assert flow.origin == info['origin']
    assert flow.data.shape == info['shape']

    for key in data.keys():
        assert np.array_equal(flow.data[key].ravel(), data[key].ravel())

    filename_reference = os.path.join(FIXTURE_DIR, 'reference_0.npy')
    reference_data = np.load(filename_reference)

    for key in reference_data.dtype.names:
        assert np.array_equal(flow.data[key], reference_data[key])


def test_reading_file_with_gz_extension_extracts_with_gunzip():
    fn_unzip = os.path.join(FIXTURE_DIR, 'flow_field0.dat')
    fn_gzip = os.path.join(FIXTURE_DIR, 'flow_field0.dat.gz')

    data_gzip, info_gzip = _read_data(fn_gzip)
    data_unzip, info_unzip = _read_data(fn_unzip)

    assert data_unzip.keys() == data_gzip.keys()
    for vals_unzip, vals_gzip in zip(data_unzip, data_gzip):
        assert np.array_equal(vals_unzip, vals_gzip)

    assert info_unzip.keys() == info_gzip.keys()
    for head_unzip, head_gzip in zip(info_unzip, info_gzip):
        assert head_unzip == head_gzip
