"""Functions and decorators for plotting graphs."""


import matplotlib.pyplot as plt
import numpy as np


def apply_clim(flow, clim, label, info=None):
    """Keep only bins where the `label` value is within `clim = (min, max)`.

    If an `info` dictionary is supplied its `shape` will be updated
    to contain the updated shape after cutting.

    """

    def calc_shape(inds):
        nx, ny = inds.shape

        x0 = None
        y0 = None

        i = 0
        while i < nx:
            column = inds[i, :]

            if column.any():
                x1 = i
                if x0 == None:
                    x0 = i

            i += 1

        i = 0
        while i < ny:
            row = inds[:, i]

            if row.any():
                y1 = i
                if y0 == None:
                    y0 = i

            i += 1

        try:
            nx = x1 - x0 + 1
        except:
            nx = 0

        try:
            ny = y1 - y0 + 1
        except:
            ny = 0

        return nx, ny

    if clim == None:
        return flow

    cmin, cmax = clim

    if cmin == None:
        cmin = -np.inf

    if cmax == None:
        cmax = np.inf

    inds = (flow[label] >= cmin) & (flow[label] <= cmax)

    if info != None:
        inds_reshaped = inds.reshape(info['shape'])
        info['shape'] = calc_shape(inds_reshaped)

    for l in flow.keys():
        flow[l] = flow[l][inds]

    return flow


def decorate_graph(func):
    """Decorator which sets up Axes for figure drawing functions.

    Args:
        func: Function to decorate (see below for requirements)

    Returns:
        (fig, ax): Tuple with created and/or used `Figure` and `Axes`

    Functions which are decorated with this function should:

     * Accept the drawing `Axes` object as their first positional argument
     * Return a `ScalarMappable` to be used for `ColorBar` creation
       (if applicable)
     * Additional positional and keyword arguments not used by the decorator
       are forwarded to the decorated function.

    If both the decorator and decorated functions share keyword arguments,
    the decorator will not forward them. Such arguments can be forwarded
    using the `extra_kwargs` keyword argument.

    The decorator by default creates a new `Figure` and `Axes` to draw in.
    An already created `Axes` can be supplied with the `use_ax` keyword
    argument.

    """

    def inner(
            *func_args,
            use_ax=None,
            title=None,
            xlabel=None,
            ylabel=None,
            xlim=(None, None),
            ylim=(None, None),
            axis=None,
            colorbar=False,
            colorbar_label=None,
            colorbar_axis_kwargs={},
            dpi=None,
            show=True,
            save=None,
            tight_layout=False,
            transparent=False,
            extra_kwargs={},
            **func_kwargs):
        if use_ax:
            ax = use_ax
            fig = ax.get_figure()
        else:
            fig, ax = plt.subplots(dpi=dpi)

        if colorbar:
            cax = _add_colorbar_axis(ax, **colorbar_axis_kwargs)

        sm = func(ax, *func_args, **extra_kwargs, **func_kwargs)

        if axis:
            ax.axis(axis)

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        if colorbar:
            plt.colorbar(sm, label=colorbar_label, cax=cax)

        if tight_layout and (not use_ax):
            fig.tight_layout()

        if save and (not use_ax):
            plt.savefig(save, transparent=transparent)

        if show and (not use_ax):
            plt.show()

        return fig, ax

    return inner


def _add_colorbar_axis(ax, position="right", size="8%", pad=0.10, **kwargs):
    """Add and return a colorbar `Axes` besides the input `Axes`."""

    from mpl_toolkits.axes_grid1 import make_axes_locatable

    divider = make_axes_locatable(ax)

    cax = divider.append_axes(position, size=size, pad=pad, **kwargs)
    fig = ax.get_figure()
    fig.add_axes(cax)

    return cax