import copy

def average_data(data_list):
    """Average a given list of flow fields.

    The flow fields must be of identical shape and be regular. It is further
    assumed that they have the same origin and bin spacing, and that the bins 
    have the same index ordering. The `read_data` function reads the data in
    such a format and is compatible with this function.

    If the input list is empty, `None` is returned.

    """

    try:
        data = copy.deepcopy(data_list[0])
    except IndexError:
        return None

    for d in data_list[1:]:
        data['M'] += d['M']
        data['N'] += d['N']

        # Averaging the actual temperature properly requires access to the number 
        # of degrees of freedom for atoms in the bin, which we do not have. We 
        # thus simply take the arithmetic mean.
        data['T'] += d['T']

        # Velocities are mass-averaged.
        data['U'] += d['M'] * d['U']
        data['V'] += d['M'] * d['V']

    num_data = float(len(data_list))

    # We do not want to divide the velocities with 0. Thus we set the mass in these 
    # bins to a number. Since no data is present in the bins, the velocities will be 0
    # after the division.
    mass_div = copy.deepcopy(data['M'])
    mass_div[mass_div == 0.] = num_data

    data['U'] /= mass_div
    data['V'] /= mass_div

    data['M'] /= num_data
    data['N'] /= num_data
    data['T'] /= num_data

    return data
