import numpy as np

from gmx_flow import GmxFlow, GmxFlowVersion
from gmx_flow.flow import convert_gmx_flow_1_to_2


def init_data_record(shape, spacing, data_fields=['M']):
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


def test_convert_version_1_to_2_divides_mass_field_by_volume():
    shape = 10, 5
    dx = 1.
    dy = 2.
    width = 5.
    bin_volume = dx * dy * width

    data = init_data_record(shape, (dx, dy))
    version = GmxFlowVersion(1)

    flow = GmxFlow(data, shape=shape, spacing=(dx, dy), version=version)
    flow_converted = convert_gmx_flow_1_to_2(flow, width)

    assert np.array_equal(flow_converted.data['X'], flow.data['X'])
    assert np.array_equal(
        flow_converted.data['M'], flow.data['M'] / bin_volume)


def test_convert_format_sets_new_version():
    shape = 10, 5
    spacing = 1., 2.

    data = init_data_record(shape, spacing)
    version = GmxFlowVersion(1)

    flow = GmxFlow(data, shape=shape, spacing=spacing, version=version)
    flow_converted = convert_gmx_flow_1_to_2(flow, 5.)

    assert flow_converted.version == GmxFlowVersion(2)


def test_convert_from_2_to_2_returns_copy_not_reference():
    shape = 10, 5
    spacing = 1., 2.

    data = init_data_record(shape, spacing)
    version = GmxFlowVersion(2)

    flow = GmxFlow(data, shape=shape, spacing=spacing, version=version)
    flow_converted = convert_gmx_flow_1_to_2(flow, 5.)

    assert flow_converted.version == GmxFlowVersion(2)
    assert not (flow_converted.data is flow.data)
