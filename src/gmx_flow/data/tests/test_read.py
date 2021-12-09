import numpy as np
import os

from gmx_flow.data.read import read_data, read_gmx_flow

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_files',
    )

def test_read_gmx_flow_is_consistent_with_read_data():
    filename = os.path.join(FIXTURE_DIR, 'flow_field0.dat')

    flow = read_gmx_flow(filename)
    data, info = read_data(filename)

    assert flow.shape == info['shape']
    assert flow.spacing == info['spacing']
    assert flow.origin == info['origin']
    assert flow.data.shape == info['shape']

    filename_reference = os.path.join(FIXTURE_DIR, 'reference_0.npy')
    reference_data = np.load(filename_reference)
    assert np.array_equal(flow.data, reference_data)
