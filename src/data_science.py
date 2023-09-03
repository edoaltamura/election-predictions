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
import os
import pandas as pd
from typing import Optional
from tqdm.auto import tqdm

from .io import IO
from .configuration import cfg_paths
from .pipeline import measure, development


class DataScience(IO):

    def __init__(self, df: pd.DataFrame, split_basename: str = 'pollster_split') -> None:
        super().__init__()
        self.data = df
        self.split_basename = split_basename

    def get_split_file_path(self, pollster_name: str) -> str:

        _pollster_join_name = '-'.join(pollster_name.split())
        _pollster_join_name = f"{self.split_basename:s}_{_pollster_join_name:s}.csv"

        return os.path.join(cfg_paths.data.interim, _pollster_join_name)

    def load_pollster_from_file(self, pollster_name: str) -> pd.DataFrame:

        file_path = self.get_split_file_path(pollster_name)

        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"File for pollster '{pollster_name:s}' not found in the interim data directory. Check "
                "that the interim directory is correctly configured, or check that the "
                "`DataScience.split_pollsters()` function was called.")

        return self.read_csv(file_path)

    def split_pollsters(self, resample: bool = True, **kwargs) -> None:

        # First get the unique names of pollsters
        unique_pollsters = self.data['Pollster'].unique()

        for pollster in (pbar := tqdm(unique_pollsters)):

            # Dynamically display the pollster being searched
            pbar.set_description(f"Splitting '{pollster:s}'")

            # Get the subset corresponding to a particular pollster
            pollster_split = self.data.loc[self.data['Pollster'] == pollster]

            if resample:
                pollster_split = self.regularise_time_series(pollster_split, **kwargs)

            # Save it to interim data directory
            self.to_csv(pollster_split, self.get_split_file_path(pollster))

    @staticmethod
    def regularise_time_series(df: pd.DataFrame, resample_every: str = '24h') -> pd.DataFrame:

        if not df['Date'].is_unique:
            raise ValueError(f"Timestamps for pollster {df['Pollster'].unique()[0]:s} have duplicates and cannot "
                             f"proceed to interpolate time series. Check the `DataEngineering.data_cleaning()` and "
                             f"its outputs, as well as the `df['Included in alternate question']` boolean.\nList of "
                             f"duplicate timestamps:\n{df[df.duplicated(subset=['Date'], keep='first')]}")

        df.index = pd.to_datetime(df['Date'])
        _resampled_data = df.resample('12h').interpolate().resample(resample_every).asfreq()

        # Non-numeric values (eg `Pollster`) are not interpolated. Fill with most recent instance.
        _resampled_data.fillna(method='ffill', inplace=True)

        return _resampled_data

    def predict(self, pollster: str):
        pass

    def dump_results(self, df: pd.DataFrame, filename: str) -> None:

        self.to_csv(df, os.path.join(cfg_paths.data.final, filename))
