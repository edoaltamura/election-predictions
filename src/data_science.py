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
from typing import Union, Optional, Dict, List
from tqdm.auto import tqdm
import numpy as np

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

    def load_pollsters_list_from_file(self) -> List[str]:

        file_path = os.path.join(cfg_paths.data.interim, f'{self.split_basename:s}_list.csv')

        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"File with the list of pollsters '{file_path:s}' not found in the interim data directory. Check "
                "that the interim directory is correctly configured, or check that the "
                "`DataScience.split_pollsters()` function was called.")

        return pd.read_csv(file_path).values.flatten().tolist()

    def split_pollsters(self, resample: bool = True, **kwargs) -> None:

        # First get the unique names of pollsters
        unique_pollsters = self.data['Pollster'].unique()

        # Save list of pollsters to file
        unique_pollsters_dump = pd.Series(unique_pollsters)
        unique_pollsters_dump.rename('Pollsters', inplace=True)
        unique_pollsters_path = os.path.join(cfg_paths.data.interim, f'{self.split_basename:s}_list.csv')
        unique_pollsters_dump.to_csv(unique_pollsters_path, index=False, header=True)

        # Use the walrus parsing technique to update the description of the pbar with the current pollster
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
        _resampled_data = df.resample('12h').interpolate(limit=14 * 4, limit_direction='forward').resample(
            resample_every).asfreq()

        # Non-numeric values (eg `Pollster`) are not interpolated. Fill with most recent instance.
        _resampled_data.loc[:, ['Pollster', 'Excludes overseas candidates']].fillna(method='ffill', inplace=True)

        return _resampled_data


    @measure
    def compute_polling_averages(self, candidates: Optional[Union[str, List[str]]] = 'all', save_plot: bool = True) -> Dict[str, pd.DataFrame]:

        _candidates_all = ['Bulstrode', 'Lydgate', 'Vincy', 'Casaubon', 'Chettam', 'Others']

        if isinstance(candidates, list):
            _candidates_selected = []

            for t in candidates:
                if t not in _candidates_all:
                    raise ValueError(f"The province {t:s} is not found in the list of available provinces. Available "
                                     f"provinces: {', '.join(_candidates_all):s}.")

                _candidates_selected.append(t)

            _candidates = _candidates_selected

        elif isinstance(candidates, str) and candidates.lower() == 'all':
            _candidates = _candidates_all

        else:
            raise ValueError(f"candidates={candidates} is not a valid type or value. Expected 'all' (default), "
                             f"or a list of strings with valid names.")

        pollsters = self.load_pollsters_list_from_file()
        polling_averages = {}
        polling_trends = {}

        for candidate in _candidates:

            df_p = self.load_pollster_from_file(pollsters[0])
            weighted_average = df_p[candidate].fillna(value=0) * df_p['Sample'].fillna(value=0)
            total_samples = df_p['Sample'].fillna(value=0)

            for pollster in pollsters[1:]:
                df_p = self.load_pollster_from_file(pollster)

                weighted_average += df_p[candidate].fillna(value=0) * df_p['Sample'].fillna(value=0)
                total_samples += df_p['Sample'].fillna(value=0)

            weighted_average /= total_samples

            # Determine rolling statistics
            weekly_average = weighted_average.rolling(window=7, win_type='gaussian').mean(std=3)
            limit = min(len(df_p['Date']), len(weighted_average), len(weekly_average))

            polling_averages['Date'] = df_p['Date'][:limit]
            polling_trends['Date'] = df_p['Date'][:limit]
            polling_averages[candidate] = weighted_average.values[:limit]
            polling_trends[candidate] = weekly_average.values[:limit]

        # Finally, convert the products to Pandas DataFrame instances
        polling_averages = pd.DataFrame(polling_averages)
        polling_trends = pd.DataFrame(polling_trends)

        if save_plot:
            pass

        return {'polling_averages': polling_averages, 'trends': polling_trends}

    def dump_results(self, dfs: Dict[str, pd.DataFrame]) -> None:

        for filename, df in dfs.items():
            df.loc[:, df.columns != 'Date'].astype(float)
            df['Date'] = pd.to_datetime(df['Date'])

            candidates_names = sorted(df.columns[df.columns != 'Date'])
            candidates_names = ['Date'] + candidates_names

            df = df.reindex(candidates_names, axis=1)

            file_path = os.path.join(cfg_paths.data.final, f'{filename:s}.csv')

            if 'average' in filename:
                self.to_csv(df, file_path)
            else:
                df.to_csv(file_path, index=True, header=True)
