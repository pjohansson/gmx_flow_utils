import numpy as np

from scipy import ndimage
from typing import Sequence

from .gmxflow import GmxFlow


def supersample(flow: GmxFlow,
                N: float | int,
                labels: Sequence[str] | None = None,
                xlabel: str = 'X',
                ylabel: str = 'Y',
                ) -> GmxFlow:
    """Increase the bin resolution by a factor N through resampling.

    This obviously does not create any new data, but the increased
    resolution can make for nicer looking images with smooth edges.

    By default all fields are resampled and returned. By supplying
    a single label or a sequence of labels using the `labels` kwarg,
    only those labels will be resampled and returned (along with
    the positional labels `X` and `Y`).

    Returns:
        GmxFlow: Supersampled flow field.

    """

    def get_coords_1d(x0, dx, nx, N):
        return x0 + (dx / float(N)) * np.arange(nx * N)

    def get_coords(N):
        x0, y0 = flow.origin
        dx, dy = flow.spacing
        nx, ny = flow.shape

        x = get_coords_1d(x0, dx, nx, N)
        y = get_coords_1d(y0, dy, ny, N)

        xs, ys = np.meshgrid(x, y, indexing='ij')

        return xs, ys

    def create_supersampled_grid(labels):
        new_shape = int(N) * nx, int(N) * ny

        dtype = [(l, float) for l in ['X', 'Y'] + labels]
        new_grid = np.zeros(new_shape, dtype=dtype)

        xs, ys = get_coords(N)
        new_grid[xlabel] = xs
        new_grid[ylabel] = ys

        return new_grid

    # It feels natural to give `N` as an int to the function,
    # but we will use it as a float since ndimage.zoom works
    # like that
    N = float(N)

    nx, ny = flow.shape
    dx, dy = flow.spacing

    if labels == None:
        # Skip position fields for supersampling
        labels = flow.fields.difference([xlabel, ylabel])
    else:
        if type(labels) == str:
            labels = [labels]

        # Ensure that no `None` type exist in the final set, since
        # that might be given for the cutoff label values
        labels = set(labels).difference([None])
        labels = list(labels)

    new_grid = create_supersampled_grid(labels)

    for key in labels:
        data = flow.data[key].reshape(flow.shape)

        # `grid-wrap` mimics PBC which is usually what we would want
        new_grid[key] = ndimage.zoom(data, N, mode='grid-wrap')

    new_spacing = dx / N, dy / N

    return GmxFlow(
        new_grid,
        shape=new_grid.shape,
        spacing=new_spacing,
        version=flow.version,
        origin=flow.origin,
    )
