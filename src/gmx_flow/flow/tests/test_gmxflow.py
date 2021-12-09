import numpy as np
from gmx_flow import *


def init_data_record(shape, spacing, data_fields=['M', 'U', 'V']):
    nx, ny = shape
    dx, dy = spacing

    x = dx * np.arange(nx)
    y = dy * np.arange(ny)
    xs, ys = np.meshgrid(x, y, indexing='ij')

    dtype = [(label, float) for label in ['X', 'Y'] + data_fields]
    data = np.zeros((nx, ny), dtype=dtype)

    data['X'] = xs
    data['Y'] = ys

    for label in data_fields:
        data[label] = np.random.random(data.shape)

    return data


def test_init_gmx_flow_sets_data():
    shape = (10, 5)
    spacing = (1., 1.)

    data = init_data_record(shape=shape, spacing=spacing)
    flow = GmxFlow(data.copy(), shape=shape, spacing=spacing)

    for l in data.dtype.names:
        assert np.array_equal(flow.data[l], data[l])


def test_init_gmx_flow_sets_shape_and_spacing():
    shape = (10, 5)
    spacing = (3., 5.)

    data = init_data_record(shape=shape, spacing=spacing)
    flow = GmxFlow(data, shape=shape, spacing=spacing)

    assert flow.shape == shape
    assert flow.spacing == spacing


def test_init_gmx_flow_reshapes_data_array():
    shape = (10, 5)
    spacing = (3., 5.)

    data = init_data_record(shape=shape, spacing=spacing)

    data_1d = data.ravel()
    assert data_1d.ndim == 1

    flow = GmxFlow(data_1d, shape=shape, spacing=spacing)
    assert flow.data.shape == shape


def test_init_gmx_flow_sets_record_fields():
    shape = (10, 5)
    spacing = (3., 5.)

    data_fields = ['M', 'T', 'N', 'U', 'V', 'extra']
    data = init_data_record(shape=shape, spacing=spacing,
                            data_fields=data_fields)

    flow = GmxFlow(data, shape=shape, spacing=spacing)

    all_fields = ['X', 'Y', 'flow'] + data_fields
    assert set(flow.fields) == set(all_fields)


def test_init_gmx_flow_sets_available_common_accessors():
    shape = (10, 5)
    spacing = (3., 5.)

    data_fields = ['M', 'U', 'V']
    data = init_data_record(shape=shape, spacing=spacing,
                            data_fields=data_fields)
    flow = GmxFlow(data, shape=shape, spacing=spacing)

    assert np.array_equal(flow.x, flow.data['X'])
    assert np.array_equal(flow.y, flow.data['Y'])
    assert np.array_equal(flow.u, flow.data['U'])
    assert np.array_equal(flow.v, flow.data['V'])
    assert np.array_equal(flow.mass, flow.data['M'])


def test_init_gmx_flow_adds_flow_magnitude():
    shape = (10, 5)
    spacing = (3., 5.)

    data_fields = ['M', 'U', 'V']
    data = init_data_record(shape=shape, spacing=spacing,
                            data_fields=data_fields)
    flow = GmxFlow(data, shape=shape, spacing=spacing)
    assert 'flow' in flow.fields

    magnitude = np.sqrt(flow.data['U']**2 + flow.data['V']**2)
    assert np.all(np.isclose(flow.data['flow'], magnitude))
    assert np.array_equal(flow.flow, flow.data['flow'])


def test_init_gmx_flow_does_not_add_magnitude_if_flow_is_not_present():
    shape = (10, 5)
    spacing = (3., 5.)

    data_fields = ['M']
    data = init_data_record(shape=shape, spacing=spacing,
                            data_fields=data_fields)
    flow = GmxFlow(data, shape=shape, spacing=spacing)

    assert 'flow' not in flow.fields
    assert 'flow' not in flow.data.dtype.names


def test_copy_gmx_flow_returns_deep_copy():
    shape = (10, 5)
    spacing = (3., 5.)

    data = init_data_record(shape=shape, spacing=spacing)

    flow = GmxFlow(data, shape=shape, spacing=spacing)
    flow2 = flow.copy()

    assert not (flow is flow2)
    assert not (flow.data is flow2.data)
    assert not (flow._backup_data is flow2._backup_data)

    assert np.array_equal(flow.data, flow2.data)
    assert np.array_equal(flow._backup_data, flow2._backup_data)

    # finally, assert that flow2.data is a view into flow2._backup_data
    flow2._backup_data['M'] *= 2.
    assert np.array_equal(flow2.data['M'], flow2._backup_data['M'])


def test_gmx_flow_shape_is_xy_indexing():
    shape = (10, 5)
    spacing = (3., 5.)

    nx, ny = shape
    dx, dy = spacing
    x = dx * np.arange(nx)
    y = dy * np.arange(ny)

    data = init_data_record(shape=shape, spacing=spacing)
    flow = GmxFlow(data, shape=shape, spacing=spacing)

    assert np.array_equal(x, flow.data['X'][:, 0])
    assert np.array_equal(y, flow.data['Y'][0, :])


def test_gmx_flow_set_xlims_changes_data_and_shape():
    shape = (10, 10)
    spacing = (1., 1.)

    data = init_data_record(shape=shape, spacing=spacing)
    flow = GmxFlow(data, shape=shape, spacing=spacing)

    xmin = 4.5
    xmax = 8.5
    flow.set_xlim(xmin, xmax)

    assert flow.shape == (4, 10)
    assert flow.data.shape == (4, 10)

    assert np.array_equal(flow.x, flow.data['X'])

    assert np.all((flow.x >= xmin) & (flow.x <= xmax))


def test_gmx_flow_set_ylims_changes_data_and_shape():
    shape = (10, 10)
    spacing = (1., 1.)

    data = init_data_record(shape=shape, spacing=spacing)
    flow = GmxFlow(data, shape=shape, spacing=spacing)

    flow.set_ylim(4.5, 8.5)

    assert flow.shape == (10, 4)
    assert flow.data.shape == (10, 4)

    assert np.array_equal(flow.y, flow.data['Y'])
