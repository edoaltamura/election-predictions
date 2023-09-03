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


class IO:

    def __init__(self) -> None:
        """
        Custom I/O Operations for Pandas DataFrames.

        This class provides custom I/O operations for Pandas DataFrames, allowing you to save
        DataFrames to CSV files while preserving column data types and read CSV files with
        explicitly allocated data types and date column parsing.

        Example usage:
            ```python
            import pandas as pd

            # Create a sample DataFrame
            data = {
                'Name': ['Alice', 'Bob', 'Charlie'],
                'Age': [25, 30, 35],
                'City': ['New York', 'San Francisco', 'Los Angeles']
            }

            df = pd.DataFrame(data)

            # Specify the path where you want to save the CSV file
            csv_path = 'sample_data.csv'

            # Use the custom to_csv method to save the DataFrame to a CSV file
            custom_io = IO()
            custom_io.to_csv(df, csv_path)

            # Now, let's read the CSV file back into a DataFrame to verify the data types preservation
            loaded_df = custom_io.read_csv(csv_path)

            # Display the loaded DataFrame
            print(loaded_df)

            # Check the data types of the loaded DataFrame
            print(loaded_df.dtypes)
            ```
        """
        pass

    @staticmethod
    def to_csv(df: pd.DataFrame, path: str) -> None:
        """
        Save a Pandas DataFrame to a CSV file while preserving column data types.

        This method is designed to extend the functionality of the Pandas `to_csv` method
        by explicitly saving the data types of each column in the CSV file. It does so by
        prepending a row of data types to the DataFrame before saving it to the CSV file.

        :param df: Input DataFrame to be saved to a CSV file.
        :param path: File path where the CSV file will be saved.
        :return: None

        Note:
            To preserve column data types, this method inserts a row containing data types
            at the beginning of the DataFrame before saving it to the CSV file. This approach
            differs from a previously used method (now deprecated), which appended data types
            to the end of the DataFrame.

        Reference:
            https://stackoverflow.com/a/43408736/7607701

        """
        dtypes_addon = []
        dtypes_addon.insert(0, dict(zip(df.columns.tolist(), df.dtypes.tolist())))
        dtypes_addon = pd.DataFrame(dtypes_addon)

        # Concatenate the mini-DataFrame with dtypes and then append the rest of the data
        _df = pd.concat([dtypes_addon, df], ignore_index=True)

        # Then save it to a csv
        _df.to_csv(path, index=False)

    @staticmethod
    def read_csv(path: str) -> pd.DataFrame:
        """
        Read a CSV file while explicitly allocating data types and parsing date columns.

        This method extends the functionality of the Pandas `read_csv` method by reading
        the second line of the CSV file to determine column data types and parsing date columns
        when appropriate. It then reads the full CSV file using these explicitly allocated data types.
        It detects the `datetime64[ns]` type and reads it as an `object` instance. This process is
        required by Pandas. Then, uses the `parse_dates` kwargs to convert it to the correct type.

        :param path: File path to the CSV file to be read.
        :return: DataFrame containing the data from the CSV file.
        """
        dtypes = {}
        parse_dates = []
        for k, v in pd.read_csv(path, nrows=1).iloc[0].to_dict().items():

            if 'datetime64[ns]' in v:
                dtypes[k] = 'object'
                parse_dates.append(k)
            else:
                dtypes[k] = v

        # Read the rest of the lines with the types from above
        # Skipping row 1 avoids importing the dtypes line
        return pd.read_csv(path, parse_dates=parse_dates, dtype=dtypes, skiprows=[1])
