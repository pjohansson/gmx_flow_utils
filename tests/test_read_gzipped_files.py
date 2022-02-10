import numpy as np
import os

from gmx_flow import read_flow, GmxFlow

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_files',
)

def test_gzipped_data_is_read_and_consistent_with_original():
    fn_unzip = os.path.join(FIXTURE_DIR, 'flow_field.dat')
    fn_gzip = os.path.join(FIXTURE_DIR, 'flow_field.dat.gz')

    data_unzip = read_flow(fn_unzip)
    data_gzip = read_flow(fn_gzip)

    assert np.array_equal(data_unzip.data, data_gzip.data)
