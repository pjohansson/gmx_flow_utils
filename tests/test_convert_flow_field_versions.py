import numpy as np

from gmx_flow import convert_gmx_flow_1_to_2


def test_convert_version_1_to_2_divides_mass_field_by_volume():
    xs = np.arange(10)
    ms = np.random.random(10)

    info = {
        'shape': (2, 5),
        'spacing': (1.0, 2.0),
        'format': 'GMX_FLOW_1',
        'origin': (0., 0.),
    }

    dx, dy = info['spacing']
    width = 5.
    volume = dx * dy * width

    data = {
        'X': xs,
        'M': ms,
    }

    data_converted, info_converted = convert_gmx_flow_1_to_2(data, info, width)

    assert np.array_equal(data_converted['X'], xs)
    assert np.array_equal(data_converted['M'], ms / volume)


def test_convert_format_does_not_modify_input():
    xs = np.arange(10)
    ms = np.random.random(10)

    info = {
        'spacing': (1.0, 2.0),
        'format': 'GMX_FLOW_1',
    }

    data = {
        'X': xs.copy(),
        'M': ms.copy(),
    }

    width = 5.
    _, _ = convert_gmx_flow_1_to_2(data, info, width)

    assert np.array_equal(data['X'], xs)
    assert np.array_equal(data['M'], ms)


def test_convert_format_sets_new_format_in_info():
    xs = np.arange(10)
    ms = np.random.random(10)

    info = {
        'spacing': (1.0, 2.0),
        'format': 'GMX_FLOW_1',
    }

    data = {
        'X': xs.copy(),
        'M': ms.copy(),
    }

    width = 5.
    _, info_converted = convert_gmx_flow_1_to_2(data, info, width)

    assert info_converted['format'] == 'GMX_FLOW_2'


def test_convert_from_2_to_2_returns_copy_not_reference():
    xs = np.arange(10)
    ms = np.random.random(10)

    info = {
        'spacing': (1.0, 2.0),
        'format': 'GMX_FLOW_2',
    }

    data = {
        'X': xs.copy(),
        'M': ms.copy(),
    }

    width = 5.
    data_return, info_return = convert_gmx_flow_1_to_2(data, info, width)

    assert id(data) != id(data_return)
    assert id(info) != id(info_return)
