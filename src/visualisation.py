import pandas as pd
import numpy as np

from data_engineering import read_csv, clean_data_file
from configuration import path_reports

df = read_csv(clean_data_file)
print(df.dtypes)

from matplotlib import pyplot as plt

plt.style.use('mplstyles/economist_xyplot.mplstyle')
fig, ax = plt.subplots()
ax.plot(df['Date'], df['Sample'].cumsum())

# Reformat x-axis tick labels
ax.xaxis.set_tick_params(labelsize=11)  # Set tick label size

ax.yaxis.set_tick_params(pad=-8,  # Pad tick labels so they don't go over y-axis
                         labeltop=True,  # Put y-axis labels on top
                         labelbottom=False,  # Set no y-axis labels on bottom
                         bottom=False,  # Set no ticks on bottom
                         labelright=False,
                         labelsize=11)  # Set tick label size

# Add labels for USA and China
# ax.text(x=.62, y=.68, s='United States', transform=fig.transFigure, size=10, alpha=.9)
# ax.text(x=.7, y=.4, s='China', transform=fig.transFigure, size=10, alpha=.9)

# Add in line and tag
ax.plot([0.12, .9],  # Set width of line
        [.98, .98],  # Set height of line
        transform=fig.transFigure,  # Set location relative to plot
        clip_on=False,
        color='#E3120B',
        linewidth=.6)
ax.add_patch(plt.Rectangle((0.12, .98),  # Set location of rectangle by lower left corder
                           0.04,  # Width of rectangle
                           -0.02,  # Height of rectangle. Negative so it goes down.
                           facecolor='#E3120B',
                           transform=fig.transFigure,
                           clip_on=False,
                           linewidth=0))

# Add in title and subtitle
ax.text(x=0.12, y=.91, s="Dataland 2024 elections", transform=fig.transFigure, ha='left', fontsize=13, weight='bold',
        alpha=.8)
ax.text(x=0.12, y=.86, s="Pollster live data, 2023-2024", transform=fig.transFigure, ha='left',
        fontsize=11, alpha=.8)

# Set source text
ax.text(x=0.12, y=0.01, s="""Source: "Dataland political archive" via ${The~Economist}$""", transform=fig.transFigure,
        ha='left', fontsize=9, alpha=.7)

# plt.tight_layout()

fig.savefig(f'../{path_reports}/test.pdf')
