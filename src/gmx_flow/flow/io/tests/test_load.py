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
