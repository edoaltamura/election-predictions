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
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from .configuration import cfg_paths
from .pipeline import measure, development
from .io import IO

URL: str = "https://cdn-dev.economistdatateam.com/jobs/pds/code-test/index.html"


class DataEngineering(IO):

    def __init__(self, url: str = URL, path: Optional[str] = None, filename: str = "dataland_polling.csv",
                 reset: bool = False, save_copy_in_final: bool = True) -> None:
        """
        Initialize a DataEngineering instance for data loading and cleaning.

        This class extends the functionality of the IO class and provides methods to load data from a URL, clean it,
        and save it to a file.

        :param url: The URL from which to load data.
        :param path: The path where the data files will be saved.
        :param filename: The name of the data file.
        :param reset: If True, reset and reload the data even if it exists.
        :param save_copy_in_final: If True, also saves a copy of the clean dataset in the `final` data directory.
        """
        super().__init__()
        self.url = url
        self.path = path
        self.filename = filename

        self.raw_data_file = os.path.join(cfg_paths.data.raw, self.filename)
        if not os.path.isfile(self.raw_data_file) or reset:
            # Initialise empty dataframe
            self.data = pd.DataFrame()
            self.load_from_url()

        self.clean_data_file = os.path.join(cfg_paths.data.interim, self.filename)
        if not hasattr(self, 'data'):
            self.data = self.load_from_file()

        if not os.path.isfile(self.clean_data_file) or reset:
            self.clean_data()

        self.save_clean_data(save_copy_in_final=save_copy_in_final)

    @measure
    def load_from_url(self) -> pd.DataFrame:
        """
        Load data from the specified URL.

        This method loads data from the provided URL and saves it as a CSV file. It also returns the loaded data as
        a Pandas DataFrame.

        :return: DataFrame containing the loaded data.
        """
        self.data = pd.read_html(self.url)[0]
        self.data.to_csv(self.raw_data_file, index=False, na_rep='NaN', mode='w', sep=',')
        return self.data

    @staticmethod
    def validate_url(url: str):
        """
        Validate the format of a URL.

        This method validates the format of the given URL using a URLValidator.

        :param url: The URL to be validated.
        """
        validator = URLValidator(verify_exists=False)
        try:
            validator(url)
        except ValidationError as err:
            print(f"The requested URL {url} is not valid. Check the initialisation of `DataEngineering(url='...')`.",
                  err)

    def load_from_file(self) -> pd.DataFrame:
        """
        Load data from a local CSV file.

        This method reads data from a local CSV file and returns it as a Pandas DataFrame.

        :return: DataFrame containing the loaded data.
        """
        self.data = self.read_csv(self.clean_data_file)
        return self.data

    @development
    def clean_data(self) -> pd.DataFrame:
        """
        Clean and preprocess the loaded data in place.

        This method performs data cleaning and preprocessing operations on the loaded data. It handles various tasks
        such as handling missing values, data type conversions, and sorting.

        Note: This method is decorated with a development decorator (eg @development) for development purposes.

        :return: DataFrame containing the cleaned data.

        Example usage:
            ```python
            data_engineering = DataEngineering(url='https://example.com/data.csv')
            cleaned_data = data_engineering.clean_data() # To return a copy of the DataFrame
            cleaned_data = data_engineering.data # To generate the cleaned DataFrame in place and get it as attribute
            ```
        """
        if self.data.empty:
            self.data = pd.read_csv(self.raw_data_file)

        # Create a new column with True for rows containing '*' and False otherwise
        self.data['Excludes overseas candidates'] = self.data['Sample'].str.contains('\*', regex=True)
        self.data['Sample'] = self.data['Sample'].str.replace('\*', '', regex=True).str.replace(',', '')
        self.data['Sample'] = pd.to_numeric(self.data['Sample'], errors='coerce', downcast='integer')

        self.data['Included in alternate question'] = self.data['Chettam'].str.contains('\*\*', regex=True)
        self.data['Included in alternate question'].fillna(False, inplace=True)

        # Convert percentage signs into fractions
        for col in ['Bulstrode', 'Lydgate', 'Chettam', 'Vincy', 'Casaubon', 'Others']:

            # Default formatting has the % sign, so detect the elements that have it to flag those that do not.
            mask = self.data[col].str.contains('%', na=False)

            # `Chettam` contains double asterisks and requires additional processing
            if col == 'Chettam':
                self.data[col] = self.data[col].str.replace('\*\*', '', regex=True).str.rstrip('%')
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce', downcast='float') / 100.0

            else:
                self.data[col] = self.data[col].str.rstrip('%').astype('float') / 100.0

            # Detect and print messages for badly formatted rows
            badly_formatted_rows = self.data.loc[~mask]

            if not badly_formatted_rows.empty:
                print(f"Found {len(badly_formatted_rows):d} badly formatted rows in column '{col}':")

        self.data['Date'] = pd.to_datetime(self.data['Date'], format='%m/%d/%y')
        self.data['Pollster'] = self.data['Pollster'].apply(str)

        # Account for double counts
        if self.data['Included in alternate question'].any():
            print('Some pollsters have given multiple responses:')

            duplication_criteria = ['Date', 'Pollster', 'Sample']

            last = self.data[self.data.duplicated(subset=duplication_criteria, keep='first')]
            print(f"\t{last['Pollster'].unique()}")
            assert last['Included in alternate question'].all()

            first = self.data[self.data.duplicated(subset=duplication_criteria, keep='last')]
            assert last['Included in alternate question'].all()
            last.index = first.index

            # Copy the missing value from the other answer
            last.loc[first.index, 'Chettam'] = first['Chettam']

            # Drop the old answer and keep only the most recent. If not done, it will create duplicate `Date` labels.
            self.data.loc[last.index] = last
            self.data.drop(index=first.index, inplace=True)
            print(
                (f"Considering only the most recent information:\n\t{last['Date'].tolist()}"
                 "\nDropping rows: {first.index}")
            )

            # Subsets not needed anymore - free up some memory.
            del first, last

        self.data.reset_index(drop=True, inplace=True)
        self.data.drop(['Included in alternate question'], inplace=True, axis=1)

        # Sort by date and group by pollster
        self.data.sort_values(['Pollster', 'Date'], ignore_index=True, inplace=True)
        self.data.reset_index(drop=True, inplace=True)

        return self.data

    def save_clean_data(self, save_copy_in_final: bool = True) -> None:
        """
        Save the cleaned data to a CSV file and optionally save a copy in the final data directory.

        :param save_copy_in_final: Whether to save a copy of the cleaned data in the final data directory. Defaults to True.

        Example usage:
            ```python
            data_engineering = DataEngineering(url='https://example.com/data.csv')

            # Save the cleaned data to a CSV file (default behavior).
            data_engineering.save_clean_data()

            # Save the cleaned data to a CSV file and skip saving a copy in the final data directory.
            data_engineering.save_clean_data(save_copy_in_final=False)
            ```
        """

        self.to_csv(self.data, self.clean_data_file)

        if save_copy_in_final:
            self.data.to_csv(os.path.join(cfg_paths.data.final, 'polls.csv'))
