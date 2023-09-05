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
import sys
import os
import pandas as pd
from typing import Union, Optional, Dict, List
from tqdm.auto import tqdm
from warnings import warn

from .io import IO
from .configuration import cfg_paths


class DataScience(IO):

    def __init__(self, df: pd.DataFrame, regularise: bool = True, split_basename: str = 'pollster_split') -> None:
        """
        DataScience class for analyzing polling data.

        This class provides functionality for analyzing polling data, including splitting data by pollster,
        computing polling averages, and dumping results to files.

        :param df: Input DataFrame containing polling data.
        :param regularise: Boolean flag indicating whether to regularize time series data (default is True).
        :param split_basename: Base name for split files (default is 'pollster_split').
        :raises FileNotFoundError: If required files are not found in the interim data directory.
        """
        super().__init__()
        self.data = df
        self.split_basename = split_basename

        self.split_pollsters(regularise=regularise)
        dfs = self.compute_polling_averages()
        self.dump_results(dfs)

    def get_split_file_path(self, pollster_name: str) -> str:
        """
        Get the file path for the split data of a specific pollster.

        :param pollster_name: Name of the pollster.
        :return: File path for the split data of the specified pollster.
        """

        _pollster_join_name = '-'.join(pollster_name.split())
        _pollster_join_name = f"{self.split_basename:s}_{_pollster_join_name:s}.csv"

        return os.path.join(cfg_paths.data.interim, _pollster_join_name)

    def load_pollster_from_file(self, pollster_name: str) -> pd.DataFrame:
        """
        Load data of a specific pollster from a file.

        :param pollster_name: Name of the pollster.
        :return: DataFrame containing the data of the specified pollster.
        :raises FileNotFoundError: If the file for the specified pollster is not found.
        """

        file_path = self.get_split_file_path(pollster_name)

        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                (f"File for pollster '{pollster_name:s}' not found in the interim data directory. Check "
                 "that the interim directory is correctly configured, or check that the "
                 "`DataScience.split_pollsters()` function was called."))

        _df = self.read_csv(file_path)
        return _df

    def load_pollsters_list_from_file(self) -> List[str]:
        """
        Load the list of pollsters from a file.

        :return: List of pollster names.
        :raises FileNotFoundError: If the list file is not found.
        """
        file_path = os.path.join(cfg_paths.data.interim, f'{self.split_basename:s}_list.csv')

        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                (f"File with the list of pollsters '{file_path:s}' not found in the interim data directory. Check "
                 "that the interim directory is correctly configured, or check that the "
                 "`DataScience.split_pollsters()` function was called."))

        return pd.read_csv(file_path).values.flatten().tolist()

    def split_pollsters(self, regularise: bool = True, **kwargs) -> None:
        """
        Split the polling data by pollster and save it to files.

        :param regularise: Boolean flag indicating whether to regularize time series data (default is True).
        :param kwargs: Additional keyword arguments for regularizing time series data.
        """
        # First get the unique names of pollsters
        unique_pollsters = self.data['Pollster'].unique()

        # Save list of pollsters to file
        unique_pollsters_dump = pd.Series(unique_pollsters)
        unique_pollsters_dump.rename('Pollsters', inplace=True)
        unique_pollsters_path = os.path.join(cfg_paths.data.interim, f'{self.split_basename:s}_list.csv')
        unique_pollsters_dump.to_csv(unique_pollsters_path, index=False, header=True)

        # Use the walrus parsing technique to update the description of the pbar with the current pollster
        for pollster in (pbar := tqdm(unique_pollsters, file=sys.stdout)):

            # Dynamically display the pollster being searched
            pbar.set_description(f"Splitting '{pollster:s}'")

            # Get the subset corresponding to a particular pollster
            pollster_split = self.data.loc[self.data['Pollster'] == pollster]

            if regularise:
                pollster_split = self.regularise_time_series(pollster_split, **kwargs)

            # Save it to interim data directory
            self.to_csv(pollster_split, self.get_split_file_path(pollster))

    @staticmethod
    def regularise_time_series(df: pd.DataFrame, resample_every: str = '24h') -> pd.DataFrame:
        """
        Regularize a time series DataFrame by interpolating missing data and resampling.

        This method regularizes a time series DataFrame by interpolating missing data points and resampling it at
        a specified frequency. It ensures that timestamps are unique and fills non-numeric columns with the most
        recent instance.

        :param df: Input time series DataFrame.
        :param resample_every: Frequency for resampling (default is '24h').
        :return: Regularized time series DataFrame.
        :raises ValueError: If timestamps have duplicates in the input DataFrame.

        Example Usage:
            ```python
            import pandas as pd

            # Create a sample time series DataFrame
            data = {
                'Date': pd.date_range(start='2023-01-01', periods=10, freq='12h'),
                'Value': [1, 2, None, 4, 5, 6, 7, None, 9, 10],
                'Pollster': ['Pollster A'] * 10
            }

            df = pd.DataFrame(data)

            # Regularize the time series DataFrame
            regularized_df = DataScience().regularise_time_series(df, resample_every='1d')
            print(regularized_df)
            ```
        """
        if not df['Date'].is_unique:
            raise ValueError((f"Timestamps for pollster {df['Pollster'].unique()[0]:s} have duplicates and cannot "
                              f"proceed to interpolate time series. Check the `DataEngineering.data_cleaning()` and "
                              f"its outputs, as well as the `df['Included in alternate question']` boolean.\nList of "
                              f"duplicate timestamps:\n{df[df.duplicated(subset=['Date'], keep='first')]}"))

        df.index = pd.to_datetime(df['Date'])

        # Interpolate the time-series and resample by a custom amount
        # TODO: the interpolate(limit=...) should computed dynamically from the first and second resampling.
        _resampled_data = df.resample('12h').interpolate(limit=14 * 4, limit_direction='forward').resample(
            resample_every).asfreq()

        # Non-numeric values (eg `Pollster`) are not interpolated. Fill with most recent instance.
        _resampled_data.loc[:, ['Pollster', 'Excludes overseas candidates']].fillna(method='ffill', inplace=True)

        return _resampled_data

    def compute_polling_averages(self, candidates: Optional[Union[str, List[str]]] = 'all') -> Dict[str, pd.DataFrame]:
        """
       Compute polling averages and trends for specified candidates.

       This method computes polling averages and trends for one or more candidates based on the available data and
       pollsters. It allows you to specify candidates by name or compute averages for all candidates.

       :param candidates: A list of candidate names or 'all' to compute averages for all candidates (default is 'all').
       :return: A dictionary containing polling averages and trends DataFrames.
       :raises ValueError: If the candidates argument is invalid.
       :raises FileNotFoundError: If required data files are missing.
       :raises RuntimeWarning: If a pollster provides very few reports.

       Example Usage:
           ```python
           import pandas as pd

           # Create a sample DataFrame (self.data) - Assuming you have already loaded your data
           data = pd.DataFrame(...)  # Your data should contain 'Pollster', 'Date', and candidate columns

           # Create an instance of DataEngineering
           data_science = DataScience(data)

           # Compute polling averages for specific candidates
           averages = data_science.compute_polling_averages(candidates=['Bulstrode', 'Lydgate'])

           # Access polling averages and trends DataFrames
           polling_averages = averages['polling_averages']
           trends = averages['trends']
           ```
       Summary:
       This function calculates polling averages and trends for a specified list of candidates or all candidates in
       the dataset. It loads pollster data from files, performs weighted averaging, and computes rolling statistics
       to provide insights into polling trends over time.
       """
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
            raise ValueError((f"candidates={candidates} is not a valid type or value. Expected 'all' (default), "
                              f"or a list of strings with valid names."))

        # Initialise dictionaries for averages and smoothed averages (ie trends)
        polling_averages = {}
        polling_trends = {}

        # Get the list of pollsters from the file. This is static, so get outside of the loop
        pollsters = self.load_pollsters_list_from_file()

        for candidate in (pbar := tqdm(_candidates, file=sys.stdout)):

            # Dynamically display the candidate being considered
            pbar.set_description(f"Candidate average for '{candidate:s}'")

            # Initialise the temporary `_df` dataframe that has two columns:
            # [Sample_{pollster}, {candidate}_{pollster}]
            pollster = pollsters[0]
            _df = self.load_pollster_from_file(pollster)
            _df.set_index('Date', inplace=True)
            _df = _df.loc[:, ['Sample', candidate]]
            _df.rename(columns={'Sample': f'Sample_{pollster:s}', candidate: f'{candidate:s}_{pollster:s}'},
                       inplace=True)

            for pollster in pollsters[1:]:
                _df_pollster = self.load_pollster_from_file(pollster)
                _df_pollster.set_index('Date', inplace=True)
                _df_pollster = _df_pollster.loc[:, ['Sample', candidate]]
                _df_pollster.rename(
                    columns={'Sample': f'Sample_{pollster:s}', candidate: f'{candidate:s}_{pollster:s}'},
                    inplace=True)

                # Perform an outer union with other columns: [Sample_{pollster}, {candidate}_{pollster}]
                _df = _df.join(_df_pollster, how='outer')

                if n_scarce_poll := len(_df_pollster) < 2:
                    warn(
                        (f"\nPollster '{pollster:s}' only gave {n_scarce_poll:d} reports. This behaviour is accounted "
                         f"for in the weighted averages, but you should investigate this pollster's data further."),
                        RuntimeWarning
                    )

            # Having no data is equivalent to a zero weight on Samples
            _df.fillna(0, inplace=True)

            # Drop rows with NaN index
            _df = _df[_df.index.notnull()]

            # Compute the sum of samples
            filter_col = [col for col in _df if col.startswith('Sample')]
            total_samples = _df[list(filter_col)].sum(axis=1)

            # Compute the sum of weighted polling fractions
            pollster = pollsters[0]
            weighted_average = _df[f'{candidate:s}_{pollster:s}'] * _df[f'Sample_{pollster:s}']
            for pollster in pollsters[1:]:
                weighted_average += _df[f'{candidate:s}_{pollster:s}'] * _df[f'Sample_{pollster:s}']

            # Realise the weighted average in-place
            weighted_average /= total_samples

            # Determine rolling statistics
            weekly_average = weighted_average.rolling(window=7, win_type='gaussian').mean(std=3)

            polling_averages['Date'] = _df.index
            polling_trends['Date'] = _df.index
            polling_averages[candidate] = weighted_average.values
            polling_trends[candidate] = weekly_average.values

        # Finally, convert the products to Pandas DataFrame instances
        polling_averages = pd.DataFrame(polling_averages)
        polling_trends = pd.DataFrame(polling_trends)

        return {'polling_averages': polling_averages, 'trends': polling_trends}

    def dump_results(self, dfs: Dict[str, pd.DataFrame]) -> None:
        """
        Dump computed polling results to CSV files.

        This method takes a dictionary of DataFrames and saves them to CSV files in the 'final' data directory. The
        DataFrames are modified to ensure proper formatting, sorting of columns, and then saved.

        :param dfs: A dictionary containing DataFrames to be saved.
        :return: None

        Example Usage:
            ```python
            import pandas as pd

            # Create a sample DataFrame (dfs) with polling results
            data = {
                'Date': ['2023-09-01', '2023-09-02'],
                'Candidate1': [30.5, 31.2],
                'Candidate2': [35.2, 34.8]
            }
            dfs = {'polling_averages': pd.DataFrame(data)}

            # Create an instance of DataScience
            data_science = DataScience(data)

            # Dump the results to CSV files in the 'final' data directory
            data_science.dump_results(dfs)
            ```
        """
        for filename, df in dfs.items():
            df.loc[:, df.columns != 'Date'].astype(float)
            df['Date'] = pd.to_datetime(df['Date'])

            # Sort the columns by name, as in the template outputs
            candidates_names = sorted(df.columns[df.columns != 'Date'])
            candidates_names = ['Date'] + candidates_names
            df = df.reindex(candidates_names, axis=1)

            # Save these files in the `final` data directory
            file_path = os.path.join(cfg_paths.data.final, f'{filename:s}.csv')

            print(f"Writing dataset '{filename:s}.csv' to: > {file_path:s}")
            if 'average' in filename:
                self.to_csv(df, file_path)
            else:
                df.to_csv(file_path, index=True, header=True)

    @staticmethod
    def load_trends(filename: str = 'trends.csv') -> pd.DataFrame:
        """
        Load polling trends DataFrame from a CSV file.

        This static method loads a polling trends DataFrame from a CSV file located in the 'final' data directory.

        :param filename: The name of the CSV file containing polling trends (default is 'trends.csv').
        :return: A DataFrame containing the polling trends data.
        :raises FileNotFoundError (pandas): If the specified file is not found.

        Example Usage:
            ```python

            # Load polling trends DataFrame
            trends_df = DataScience().load_trends('my_trends.csv')
            ```
        """
        file_path = os.path.join(cfg_paths.data.final, filename)
        _df = pd.read_csv(file_path)
        _df.loc[:, 'Date'] = pd.to_datetime(_df['Date'])
        return _df
