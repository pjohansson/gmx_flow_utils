import copy

def convert_gmx_flow_1_to_2(data, info, width):
    """Convert flow data from 'GMX_FLOW_1' to 'GMX_FLOW_2'.

    This changes the field 'M' to represent the mass density instead of 
    the total mass in the bin. Thus we also require the width of the system,
    in order to calculate the bin volume.

    If the `format` field in `info` is already 'GMX_FLOW_2' an unmodified 
    copy of the original data is returned.

    """

    info = copy.deepcopy(info)
    data = copy.deepcopy(data)

    if info['format'] == 'GMX_FLOW_1':
        (dx, dy) = info['spacing']
        volume = dx * dy * width

        if 'M' in data:
            data['M'] /= volume

        info['format'] = 'GMX_FLOW_2'

    return data, info
