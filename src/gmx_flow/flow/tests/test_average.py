import numpy as np
from typing import Sequence

from gmx_flow import average_data, GmxFlow


def init_data_record(shape: tuple[int, int],
                     spacing: tuple[float, float],
                     data_fields: Sequence[str] = ['M', 'U', 'V', 'N', 'T'],
                     ) -> np.ndarray:
    """Create a numpy array with coordinates and random data."""

    nx, ny = shape
    dx, dy = spacing

    x = dx * np.arange(nx)
    y = dy * np.arange(ny)
    xs, ys = np.meshgrid(x, y, indexing='ij')

    dtype = [(label, float) for label in ['X', 'Y'] + list(data_fields)]
    data = np.zeros((nx, ny), dtype=dtype)

    data['X'] = xs
    data['Y'] = ys

    for label in data_fields:
        data[label] = np.random.random(data.shape)

    return data


def assert_flow_metadata_matches(
        flow1: GmxFlow,
        flow2: GmxFlow,
):
    assert flow1.shape == flow2.shape
    assert flow1.spacing == flow2.spacing
    assert flow1.origin == flow2.origin
    assert flow1.box_size == flow2.box_size
    assert flow1.fields == flow2.fields
    assert flow1.units == flow2.units
    assert flow1.descriptions == flow2.descriptions
    assert flow1.version == flow2.version


def test_average_no_flow_fields_yields_none():
    assert average_data([]) == None


def test_average_single_flow_field_yields_identical_copy():
    shape = (10, 5)
    spacing = (1., 1.)

    data = init_data_record(shape=shape, spacing=spacing)
    flow = GmxFlow(data.copy(), shape=shape, spacing=spacing)

    avg_flow: GmxFlow = average_data([flow])  # type: ignore

    assert id(avg_flow) != id(flow)
    assert np.array_equal(avg_flow.data, flow.data)
    assert_flow_metadata_matches(avg_flow, flow)


def test_mass_and_number_of_atoms_are_averaged():
    shape = (10, 5)
    spacing = (1., 0.5)

    data1 = init_data_record(shape, spacing)
    data2 = init_data_record(shape, spacing)

    flow1 = GmxFlow(data1.copy(), shape=shape, spacing=spacing)
    flow2 = GmxFlow(data2.copy(), shape=shape, spacing=spacing)

    avg_flow: GmxFlow = average_data([flow1, flow2])  # type: ignore

    mass1 = data1['M']
    mass2 = data2['M']
    mass_avg = (mass1 + mass2) / 2.

    num1 = data1['N']
    num2 = data2['N']
    num_avg = (num1 + num2) / 2.

    assert np.array_equal(mass_avg, avg_flow.data['M'])
    assert np.array_equal(num_avg, avg_flow.data['N'])


def test_average_flow_velocities_are_mass_weighted():
    shape = (10, 5)
    spacing = (1., 0.5)

    data1 = init_data_record(shape, spacing)
    data2 = init_data_record(shape, spacing)

    flow1 = GmxFlow(data1.copy(), shape=shape, spacing=spacing)
    flow2 = GmxFlow(data2.copy(), shape=shape, spacing=spacing)

    avg_flow: GmxFlow = average_data([flow1, flow2])  # type: ignore

    us1 = data1['U']
    vs1 = data1['V']
    ms1 = data1['M']

    us2 = data2['U']
    vs2 = data2['V']
    ms2 = data2['M']

    ms_total = ms1 + ms2
    us_avg = (us1 * ms1 + us2 * ms2) / ms_total
    vs_avg = (vs1 * ms1 + vs2 * ms2) / ms_total

    assert np.array_equal(us_avg, avg_flow.data['U'])
    assert np.array_equal(vs_avg, avg_flow.data['V'])


def test_average_temperature_is_unweighted():
    shape = (10, 5)
    spacing = (1., 0.5)

    data1 = init_data_record(shape, spacing)
    data2 = init_data_record(shape, spacing)

    flow1 = GmxFlow(data1.copy(), shape=shape, spacing=spacing)
    flow2 = GmxFlow(data2.copy(), shape=shape, spacing=spacing)

    avg_flow: GmxFlow = average_data([flow1, flow2])  # type: ignore

    temp1 = data1['T']
    temp2 = data2['T']
    temp_avg = (temp1 + temp2) / 2.

    assert np.array_equal(temp_avg, avg_flow.data['T'])
