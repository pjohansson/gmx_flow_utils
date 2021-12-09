"""Functions and decorators for plotting graphs."""


import matplotlib.pyplot as plt
import numpy as np

from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.figure import Figure
from typing import Tuple, Optional, Mapping, Any, Sequence, Callable


def decorate_graph(func: Callable[[Axes, Sequence[Any]], ScalarMappable],
                   ) -> Callable[[Sequence[Any]], Tuple[Figure, Axes]]:
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
            *func_args: Sequence[Any],
            use_ax: Optional[Axes] = None,
            title: str = None,
            xlabel: str = None,
            ylabel: str = None,
            xlim: Tuple[float, float] = (None, None),
            ylim: Tuple[float, float] = (None, None),
            axis: str = None,
            colorbar: bool = False,
            colorbar_label: str = None,
            colorbar_axis_kwargs: Mapping[str, Any] = {},
            dpi: float = None,
            show: bool = True,
            save: Optional[str] = None,
            tight_layout: bool = False,
            transparent: bool = False,
            extra_kwargs: Mapping[str, Any] = {},
            **func_kwargs: Mapping[str, Any],
    ) -> Tuple[Figure, Axes]:
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


def _add_colorbar_axis(ax: Axes,
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
