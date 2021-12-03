import copy
import numpy as np

from scipy import ndimage

def supersample_data(flow, info, N, labels=None, xlabel='X', ylabel='Y'):
    """Increase the bin resolution by a factor N through resampling.

    This obviously does not create any new data, but the increased
    resolution can make for nicer looking images with smooth edges.

    By default all fields are resampled and returned. By supplying
    a single label or a sequence of labels using the `labels` kwarg,
    only those labels will be resampled and returned (along with
    the positional labels `X` and `Y`).

    Returns:
        flow, info: Updated flow and information dictionaries

    """

    def get_coords_1d(x0, dx, nx, N):
        return x0 + (dx / float(N)) * np.arange(nx * N)

    def get_coords(info, N):
        x0, y0 = info['origin']
        dx, dy = info['spacing']
        nx, ny = info['shape']

        x = get_coords_1d(x0, dx, nx, N)
        y = get_coords_1d(y0, dy, ny, N)

        xs, ys = np.meshgrid(x, y, indexing='ij')

        return xs.ravel(), ys.ravel()

    shape = info['shape']
    nx, ny = shape
    dx, dy = info['spacing']

    if labels == None:
        labels = flow.keys().difference([xlabel, ylabel])
    else:
        if type(labels) == str:
            labels = [labels]

        # Ensure that no `None` type exist in the final set, since
        # that might be given for the cutoff label values
        labels = set(labels).difference([None])

    output = {}
    for key in labels:
        data = flow[key].reshape(shape)

        # `grid-wrap` mimics PBC which is usually what we would want
        output[key] = ndimage.zoom(data, N, mode='grid-wrap').ravel()

    # Coordinates must be calculated explicitly using new spacing values.
    # This is both faster (since they are completely uniform) and more
    # accurate. In fact, resampling the coordinates leads to artifacts!
    xs, ys = get_coords(info, N)
    output[xlabel] = xs
    output[ylabel] = ys

    info_output = copy.deepcopy(info)
    info_output['shape'] = nx * N, ny * N
    info_output['num_bins'] = output[xlabel].size
    info_output['spacing'] = dx / float(N), dy / float(N)

    return output, info_output
