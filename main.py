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

from pandas import DataFrame
import sys

sys.path.append('..')

from src import DataEngineering, DataScience, PlotTimeSeries


def plot_trends(df: DataFrame) -> None:
    """
    Plot polling trends for all candidates.

    This function creates a time series plot to visualize polling trends for multiple candidates over time using
    Matplotlib.

    :param df: A DataFrame containing polling data for multiple candidates with a 'Date' column and columns for each
               candidate's polling percentages.
    :return: None

    Example Usage:
        ```python
        import pandas as pd

        # Create a sample DataFrame with polling data
        data = {
            'Date': ['2023-09-01', '2023-09-02'],
            'Bulstrode': [30.5, 31.2],
            'Lydgate': [35.2, 34.8],
            'Vincy': [25.8, 26.4],
            # Add more candidate columns as needed
        }
        polling_df = pd.DataFrame(data)

        # Plot polling trends
        plot_trends(polling_df)
        ```
    """
    plt_ts = PlotTimeSeries()
    fig, ax = plt_ts.get_panels()

    for candidate in ['Bulstrode', 'Lydgate', 'Vincy', 'Casaubon', 'Chettam', 'Others']:
        ax.plot(df['Date'], df[candidate], label=candidate)

    plt_ts.set_title('Bulstrodites trending', subtitle='Fraction of candidate polling, %/100')
    plt_ts.set_source('Dataland political archive 2023-24', pad=0.15)

    ax.legend(fontsize=10, loc='center left', frameon=True, framealpha=0.85)
    plt_ts.savefig('polling_trends.png', dpi=250)


def inspect_imported_modules() -> None:
    """
    Lists the modules used that are not included in the standard library
    :return: None
    """
    for i in sys.modules.keys():
        if not i.startswith('_') and '.' not in i and i not in sys.builtin_module_names :
            print(i)


def main() -> int:
    # Run the data engineering pipeline to clean the raw inputs
    de = DataEngineering(reset=True)  # reset=True starts from scraping the URL, False uses locally saved data.
    print('\nA glimpse of the clean data:\n', de.data.head(10))

    # Run the data science pipeline to generate the outputs
    ds = DataScience(de.data)
    trends = ds.load_trends()

    # Make a plot and visualise the trends
    plot_trends(trends)

    return 0


if __name__ == '__main__':
    main()
    # inspect_imported_modules()
