import copy

from collections.abc import Sequence

from .gmxflow import GmxFlow


def average_data(flow_fields: Sequence[GmxFlow]) -> GmxFlow:
    """Average a given list of flow fields.

    The flow fields must be of identical shape and be regular. It is further
    assumed that they have the same origin and bin spacing, and that the bins
    have the same index ordering.

    If the input list is empty, `None` is returned.

    """

    try:
        avg_flow = flow_fields[0].copy()
    except IndexError:
        return None

    for flow in flow_fields[1:]:
        avg_flow.data['M'] += flow.data['M']
        avg_flow.data['N'] += flow.data['N']

        # Averaging the actual temperature properly requires access to the number
        # of degrees of freedom for atoms in the bin, which we do not have. We
        # thus simply take the arithmetic mean.
        avg_flow.data['T'] += flow.data['T']

        # Velocities are mass-averaged.
        avg_flow.data['U'] += flow.data['M'] * flow.data['U']
        avg_flow.data['V'] += flow.data['M'] * flow.data['V']
        avg_flow.data['flow'] += flow.data['M'] * flow.data['flow']

    num_data = float(len(flow_fields))

    # We do not want to divide the velocities with 0. Thus we set the mass in these
    # bins to a number. Since no data is present in the bins, the velocities will be 0
    # after the division.
    mass_div = copy.deepcopy(avg_flow.data['M'])
    mass_div[mass_div == 0.] = num_data

    avg_flow.data['U'] /= mass_div
    avg_flow.data['V'] /= mass_div
    avg_flow.data['flow'] /= mass_div

    avg_flow.data['M'] /= num_data
    avg_flow.data['N'] /= num_data
    avg_flow.data['T'] /= num_data

    return avg_flow
