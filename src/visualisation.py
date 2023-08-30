import pandas as pd
import numpy as np
import os.path
from matplotlib import pyplot as plt

from .configuration import cfg_paths


class PlotTimeSeries:
    mplstyle: str = 'economist_xyplot.mplstyle'

    def __init__(self):
        plt.style.use(os.path.join(cfg_paths.mplstyles, self.mplstyle))

        self.fig, self.axes = plt.subplots()

    def get_panels(self):
        return self.fig, self.axes

    def format(self):

        self.set_ticks()
        self.set_head_graphics()

    def set_ticks(self):
        # Reformat x-axis tick labels
        self.axes.xaxis.set_tick_params(labelsize=11)  # Set tick label size

        self.axes.yaxis.set_tick_params(pad=-8,  # Pad tick labels so they don't go over y-axis
                                        labeltop=True,  # Put y-axis labels on top
                                        labelbottom=False,  # Set no y-axis labels on bottom
                                        bottom=False,  # Set no ticks on bottom
                                        labelright=False,
                                        labelsize=11)  # Set tick label size

        # Add labels for USA and China
        # ax.text(x=.62, y=.68, s='United States', transform=fig.transFigure, size=10, alpha=.9)
        # ax.text(x=.7, y=.4, s='China', transform=fig.transFigure, size=10, alpha=.9)

    def set_head_graphics(self):
        # Add in line and tag
        self.axes.plot([0.12, .9],  # Set width of line
                       [.98, .98],  # Set height of line
                       transform=self.fig.transFigure,  # Set location relative to plot
                       clip_on=False,
                       color='#E3120B',
                       linewidth=.6)
        self.axes.add_patch(plt.Rectangle((0.12, .98),  # Set location of rectangle by lower left corder
                                          0.04,  # Width of rectangle
                                          -0.02,  # Height of rectangle. Negative so it goes down.
                                          facecolor='#E3120B',
                                          transform=self.fig.transFigure,
                                          clip_on=False,
                                          linewidth=0))

    def set_title(self, title: str, subtitle: str = ''):
        # Add in title and subtitle
        self.axes.text(x=0.12, y=.91, s=title, transform=self.fig.transFigure, ha='left', fontsize=13,
                       weight='bold',
                       alpha=.8)
        self.axes.text(x=0.12, y=.86, s=subtitle, transform=self.fig.transFigure, ha='left',
                       fontsize=11, alpha=.8)

    def set_source(self, source: str):
        self.axes.text(x=0.12, y=0.01, s=f"""Source: "{source:s}" via ${{The~Economist}}$""",
                       transform=self.fig.transFigure,
                       ha='left', fontsize=9, alpha=.7)

    def savefig(self, filename: str, **kwargs):
        savefig_path = os.path.join(cfg_paths.reports, filename)
        print(f"Figure {filename:s} saved in reports directory.")
        self.fig.savefig(savefig_path, **kwargs)
