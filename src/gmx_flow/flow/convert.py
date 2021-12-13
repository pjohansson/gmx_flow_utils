from .gmxflow import GmxFlow, GmxFlowVersion


def convert_gmx_flow_1_to_2(flow: GmxFlow, width: float) -> GmxFlow:
    """Convert flow data from 'GMX_FLOW_1' to 'GMX_FLOW_2'.

    This changes the field 'M' to represent the mass density instead of
    the total mass in the bin. Thus we also require the width of the system,
    in order to calculate the bin volume.

    If the `version` is already 'GMX_FLOW_2' an unmodified
    copy of the original data is returned.

    """

    converted = flow.copy()

    if converted.version == GmxFlowVersion(1):
        dx, dy = converted.spacing
        bin_volume = dx * dy * width

        try:
            converted.data['M'] /= bin_volume
        except KeyError:
            pass

        converted.version = GmxFlowVersion(2)

    return converted
