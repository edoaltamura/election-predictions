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
import pandas as pd
import numpy as np
import os.path
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

from .configuration import cfg_paths


class PlotTimeSeries:
    mplstyle: str = 'economist_xyplot.mplstyle'

    def __init__(self, **kwargs):
        plt.style.use(os.path.join(cfg_paths.mplstyles, self.mplstyle))

        self.fig, self.axes = plt.subplots(**kwargs)
        self.set_ticks()

    def get_panels(self):
        return self.fig, self.axes

    def set_ticks(self, years_pad: float = 7.5, labelsize: int = 10) -> None:
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

    def set_title(self, title: str, subtitle: str = '', patch_aspect: float = 13. / 85., hspace: float = 0.03):
        """

        :param title:
        :param subtitle:
        :param patch_aspect:
        :param hspace:
        :return:
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

    def set_source(self, source: str, pad: float = 0.13):
        x0, y0, w, h = self.axes.get_position().bounds
        self.fig.text(x=x0, y=y0 - pad,
                      s=f"""Source: "{source:s}" via ${{The~Economist}}$""",
                      ha='left', va='bottom', fontsize=9, alpha=.6)

    def savefig(self, filename: str, **kwargs):
        savefig_path = os.path.join(cfg_paths.reports, filename)
        print(f"Figure {filename:s} saved in reports directory.")
        self.fig.savefig(savefig_path, **kwargs)
