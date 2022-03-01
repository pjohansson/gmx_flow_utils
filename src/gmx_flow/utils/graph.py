"""Functions and decorators for plotting graphs."""


import matplotlib.pyplot as plt

from collections.abc import Callable, Mapping
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.figure import Figure
from typing import Any, Concatenate, ParamSpec


P = ParamSpec('P')


def decorate_graph(
    func: Callable[Concatenate[Axes, P], ScalarMappable],
) -> Callable[P, tuple[Figure, Axes]]:
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

    # Examples

    Decorate a function that draws a line plot of input data:

    ```
    import numpy as np
    from gmx_flow.utils.graph import decorate_graph

    @decorate_graph
    def draw_plot(ax, xs, ys, color='red', linestyle=None):
        return ax.plot(xs, ys, color=color, linestyle=linestyle)

    xs = np.linspace(0., 2. * np.pi)
    ys = np.sin(xs)

    draw_plot(xs, ys,
              # These three kwargs are consumed by `decorate_graph`
              xlabel='x', ylabel='sin(x)', save='sine.eps',
              # This is not, so it's forwarded to the function as a kwarg
              linestyle='dashed',
              # This is neither consumed by `decorate_graph` nor used
              # by the function, so an error will be yielded
              # lineweight=3.0,
    )
    ```

    """

    def inner(
        *func_args: P.args,
        use_ax: Axes | None = None,
        title: str = None,
        xlabel: str = None,
        ylabel: str = None,
        xlim: tuple[float | None, float | None] = (None, None),
        ylim: tuple[float | None, float | None] = (None, None),
        axis: str = None,
        colorbar: bool = False,
        colorbar_label: str = None,
        colorbar_axis_kwargs: Mapping[str, Any] = {},
        dpi: float = None,
        show: bool = True,
        noclose: bool = False,
        save: str | None = None,
        legend: bool = False,
        tight_layout: bool = False,
        transparent: bool = False,
        extra_kwargs: Mapping[str, Any] = {},
        **func_kwargs: P.kwargs,
    ) -> tuple[Figure, Axes]:
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

        if legend:
            plt.legend()

        if tight_layout and (not use_ax):
            fig.tight_layout()

        if save and (not use_ax):
            plt.savefig(save, transparent=transparent)

        if show and (not use_ax):
            plt.show()

        # If the figure is neither shown nor created by the caller,
        # we destroy it after saving it to disk (disabled with `noclose`).
        # This helps with batch creation of many figures.
        if not (show or use_ax or noclose):
            plt.close(fig)

        return fig, ax

    return inner


def _add_colorbar_axis(
    ax: Axes,
    position: str = "right",
    size: str = "8%",
    pad: float = 0.10,
    **kwargs: Mapping[str, Any],
) -> Axes:
    """Add and return a colorbar `Axes` besides the input `Axes`."""

    from mpl_toolkits.axes_grid1 import make_axes_locatable

    divider = make_axes_locatable(ax)

    cax = divider.append_axes(position, size=size, pad=pad, **kwargs)
    fig = ax.get_figure()
    fig.add_axes(cax)

    return cax
