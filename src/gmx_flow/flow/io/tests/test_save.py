import numpy as np
import os
import pytest

import gmx_flow
from gmx_flow import GmxFlow

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_files',
)

# Setup a fixture which copies files into a temporary directory,
# for when we want to write to that same directory for tests
FILES = pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'flow_field0.dat'),
    os.path.join(FIXTURE_DIR, 'flow_field0.dat.gz'),
)

@FILES
def test_saving_file_creates_same_file_when_loading(datafiles):
    fn1 = datafiles / 'flow_field0.dat'
    fn2 = datafiles / 'flow_field1.dat'

    flow = gmx_flow.read_flow(fn1)
    gmx_flow.write_flow(fn2, flow)

    flow2 = gmx_flow.read_flow(fn2)

    assert np.array_equal(flow.data, flow2.data)

def test_saving_flow_with_missing_fields_yields_error(tmpdir):
    path = os.path.join(tmpdir, 'output.dat')

    nx = 10
    ny = 5
    shape = nx, ny
    spacing = 1., 1.

    dtype = [(l, float) for l in ['X', 'Y', 'M']]
    data = np.zeros((nx, ny), dtype=dtype)

    flow = GmxFlow(data, shape=shape, spacing=spacing)

    with pytest.raises(Exception) as exc:
        gmx_flow.write_flow(path, flow)

def test_saving_flow_with_extra_fields_saves_required_fields_only(tmpdir):
    path = os.path.join(tmpdir, 'output.dat')

    nx = 10
    ny = 5
    shape = nx, ny
    spacing = 1., 1.

    required_fields = ['X', 'Y', 'M', 'N', 'T', 'U', 'V']
    dtype = [(l, float) for l in required_fields + ['extra']]
    data = np.zeros((nx, ny), dtype=dtype)

    flow = GmxFlow(data, shape=shape, spacing=spacing)
    gmx_flow.write_flow(path, flow)

    flow2 = gmx_flow.read_flow(path)

    assert set(flow2.fields) < set(flow.fields)
    # `flow` is also calculated and added, but not saved
    assert set(flow2.fields) == set(required_fields + ['flow'])


@FILES
def test_saving_files_with_gz_extension_gzips_content(datafiles):
    fn1 = datafiles / 'flow_field0.dat.gz'
    fn2 = datafiles / 'flow_field1.dat.gz'

    flow = gmx_flow.read_flow(fn1)
    gmx_flow.write_flow(fn2, flow)

    flow2 = gmx_flow.read_flow(fn2)

    # assert np.array_equal(flow.data, flow2.data)
