#!/usr/bin/env python
# encoding: utf-8

"""
@Author:              Edoardo Altamura
@Year:                2023
@Email:               edoardo.altamura@outlook.com
@Copyright:           Copyright (c) 2023 Edoardo Altamura
@Last Modified by:    Edoardo Altamura
@Latest release:      5 Sep 2023
@Project:             Election predictions (Data Science with The Economist)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import numpy as np
import os.path
from typing import Tuple
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

from .configuration import cfg_paths


class PlotTimeSeries:
    """
    Example usage:
        ```python
        import pandas as pd
        import matplotlib.pyplot as plt
        from src import PlotTimeSeries  # Import the PlotTimeSeries class

        # Create a sample DataFrame (replace this with your own data)
        data = {
            'Date': pd.date_range(start='2023-01-01', periods=365),
            'Bulstrode': [0.1 * i for i in range(365)],
            'Lydgate': [0.15 * i for i in range(365)],
            'Vincy': [0.08 * i for i in range(365)],
        }

        df = pd.DataFrame(data)

        # Create an instance of PlotTimeSeries
        plt_ts = PlotTimeSeries()

        # Get the figure and axes objects
        fig, ax = plt_ts.get_panels()

        # Plot the data for each candidate
        for candidate in ['Bulstrode', 'Lydgate', 'Vincy']:
            ax.plot(df['Date'], df[candidate], label=candidate)

        # Set titles and labels
        plt_ts.set_title('Candidate Polling Trends', subtitle='Fraction of candidate polling, %/100')
        plt_ts.set_source('Dataland political archive 2023', pad=0.15)

        # Add a legend
        ax.legend(fontsize=10, loc='upper left', frameon=True, framealpha=0.85)

        # Save the plot
        plt_ts.savefig('polling_trends.png', dpi=300)

        # Show the plot (if you want to display it)
        plt.show()
        ```
    """
    mplstyle: str = 'economist_xyplot.mplstyle'

    def __init__(self, **kwargs):
        """
        Initialize a PlotTimeSeries object.

        :param kwargs: Additional keyword arguments to pass to the plt.subplots function.
        """
        plt.style.use(os.path.join(cfg_paths.mplstyles, self.mplstyle))

        self.fig, self.axes = plt.subplots(**kwargs)
        self.set_ticks()

    def get_panels(self) -> Tuple[plt.Figure, plt.Axes]:
        """
        Get the figure and axes objects.

        :return: A tuple containing the figure and axes objects.
        """
        return self.fig, self.axes

    def set_ticks(self, years_pad: float = 7.5, labelsize: int = 10) -> None:
        """
        Set custom tick parameters for the plot.

        :param years_pad: Padding for the years axis.
        :param labelsize: Tick label font size.
        :return: None
        """
        # Reformat y-axis tick labels
        self.axes.yaxis.set_tick_params(pad=-4,  # Pad tick labels so they don't go over y-axis
                                        labeltop=True,  # Put y-axis labels on top
                                        labelbottom=False,  # Set no y-axis labels on bottom
                                        bottom=False,  # Set no ticks on bottom
                                        labelright=False,
                                        labelsize=labelsize)  # Set tick label size

        # Format x-axis accounting for the time series scope
        # Minor ticks every month
        fmt_month = mdates.MonthLocator()

        # Minor ticks every year
        fmt_year = mdates.YearLocator()

        self.axes.xaxis.set_minor_locator(fmt_month)
        # '%b' to get the names of the month
        self.axes.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))
        self.axes.xaxis.set_major_locator(fmt_year)
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

        # Fontsize for month labels
        self.axes.tick_params(labelsize=labelsize, which='both')

        # Create a second x-axis beneath the first x-axis to show the year in YYYY format
        sec_xaxis = self.axes.secondary_xaxis(-years_pad / 100.)
        sec_xaxis.xaxis.set_major_locator(fmt_year)
        sec_xaxis.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

        # Hide the second x-axis spines and ticks
        sec_xaxis.spines['bottom'].set_visible(False)
        sec_xaxis.tick_params(length=0, labelsize=labelsize)

    def set_title(self, title: str, subtitle: str = '', patch_aspect: float = 13. / 85., hspace: float = 0.03) -> None:
        """
        Set the title and subtitle for the plot.

        :param title: The main title of the plot.
        :param subtitle: The subtitle of the plot.
        :param patch_aspect: Aspect ratio of the red patch.
        :param hspace: Vertical spacing between title, subtitle, and patch.
        :return: None
        """
        # Get the bounds [start(x), start(y), width, height] of the Axes canvas in Figure coordinates
        x0, y0, w, h = self.axes.get_position().bounds

        # Increment the top anchor to get position of the subtitle
        y0 += h * (1. + hspace)

        # Start from the subtitle
        # Instead of using Axes.text(..., transform=fig.transFigure), we directly use Figure.text(...)
        t = self.fig.text(x=x0, y=y0, s=subtitle, ha='left', va='bottom', fontsize=11, alpha=.8)
        renderer = self.fig.canvas.get_renderer()
        bb = t.get_window_extent(renderer=renderer).transformed(self.fig.transFigure.inverted())
        height = bb.height

        # Increment again and work way up to the title
        y0 += height + h * hspace

        # Add in title and subtitle
        t = self.fig.text(x=x0, y=y0, s=title, ha='left', fontsize=13, weight='bold', alpha=.8)

        bb = t.get_window_extent(renderer=renderer).transformed(self.fig.transFigure.inverted())
        height = bb.height

        # Increment further to get the location of the top red patch
        y0 += height + h * hspace

        # Then headline graphics
        aspect_fig = np.divide(*self.fig.get_size_inches())
        patch_aspect_factor = aspect_fig / self.fig.dpi / patch_aspect

        # Plot line next to the red rectangle
        self.axes.plot([x0, x0 + w],  # Set width of line
                       [y0] * 2,  # Set height of line
                       transform=self.fig.transFigure,  # Set location relative to plot
                       clip_on=False,
                       color='#E3120B',
                       linewidth=1)

        # Instantiate the red rectangle at the top
        top_patch = plt.Rectangle((x0, y0),  # Set location of rectangle by lower left corner
                                  1. * patch_aspect_factor,
                                  patch_aspect * patch_aspect_factor,
                                  facecolor='#E3120B',
                                  transform=self.fig.transFigure,
                                  clip_on=False,
                                  linewidth=0)
        self.axes.add_patch(top_patch)

    def set_source(self, source: str, pad: float = 0.13) -> None:
        """
        Set the data source for the plot.

        :param source: The data source to display below the plot.
        :param pad: Vertical padding between source text and plot.
        :return: None
        """
        x0, y0, w, h = self.axes.get_position().bounds
        self.fig.text(x=x0, y=y0 - pad,
                      s=f"""Source: "{source:s}" via ${{The~Economist}}$""",
                      ha='left', va='bottom', fontsize=9, alpha=.6)

    def savefig(self, filename: str, **kwargs) -> None:
        """
        Save the plot as an image file.

        :param filename: The name of the output image file.
        :param kwargs: Additional keyword arguments to pass to plt.savefig.
        :return: None
        """
        savefig_path = os.path.join(cfg_paths.reports, filename)
        print(f"Figure {filename:s} saved in reports directory.")

        self.fig.savefig(savefig_path, **kwargs)
