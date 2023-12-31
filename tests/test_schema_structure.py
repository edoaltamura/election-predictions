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
import pytest
import pandas as pd
from src import DataEngineering


@pytest.fixture
def data_engineering():
    # Create an instance of the DataEngineering class for testing
    return DataEngineering().load_from_url()


def test_empty_data_handling(data_engineering):
    # Test if the method correctly loads data when self.data is empty
    data_engineering.data = pd.DataFrame()  # Empty DataFrame
    data_engineering.clean_data()
    assert not data_engineering.data.empty


def test_cleaning_operations(data_engineering):
    # Test various cleaning operations on the data
    data_engineering.clean_data()
    assert 'Excludes overseas candidates' in data_engineering.data.columns
    assert 'Sample' not in data_engineering.data['Sample'].str.contains('*').any()
    assert 'Chettam' not in data_engineering.data['Chettam'].str.contains('**').any()
    assert 'Chettam' not in data_engineering.data['Chettam'].str.contains('%').any()
    assert 'Date' in data_engineering.data.columns
    assert 'Pollster' in data_engineering.data.columns


def test_double_counts_handling(data_engineering):
    # Test handling of double counts
    data_engineering.clean_data()
    # Assuming you have a way to set Included in alternate question to True
    data_engineering.data.loc[0, 'Included in alternate question'] = True
    with pytest.raises(AssertionError):
        data_engineering.clean_data()  # This should raise an AssertionError


def test_sorting_and_grouping(data_engineering):
    # Test sorting and grouping of data
    data_engineering.clean_data()
    assert data_engineering.data['Date'].is_monotonic_increasing
    assert data_engineering.data.groupby('Pollster').apply(lambda x: x['Date'].is_monotonic_increasing).all()


def test_missing_values_handling(data_engineering):
    # Test handling of missing values
    data_engineering.data = pd.DataFrame({'Sample': ['10', None, '20', '30']})
    data_engineering.clean_data()
    assert not data_engineering.data['Sample'].isna().any()


def test_percentage_conversion(data_engineering):
    # Test percentage sign conversion
    data_engineering.data = pd.DataFrame({'Bulstrode': ['10%', '20%', '30%']})
    data_engineering.clean_data()
    assert (data_engineering.data['Bulstrode'] == [0.1, 0.2, 0.3]).all()


def test_date_format(data_engineering):
    # Test date format conversion
    data_engineering.data = pd.DataFrame({'Date': ['01/01/21', '02/02/21', '03/03/21']})
    data_engineering.clean_data()
    assert (data_engineering.data['Date'].dt.strftime('%Y-%m-%d') == ['2021-01-01', '2021-02-02', '2021-03-03']).all()


def test_pollster_type(data_engineering):
    # Test if 'Pollster' column is of type str
    data_engineering.clean_data()
    assert data_engineering.data['Pollster'].apply(type).eq(str).all()


def test_double_asterisk_handling(data_engineering):
    # Test handling of '**' and transfer of information to the additional column
    data_engineering.data = pd.DataFrame({'Chettam': ['**', '60%', '70%']})
    data_engineering.clean_data()

    # Check if '**' is removed from the 'Chettam' column
    assert (data_engineering.data['Chettam'] == [None, '60%', '70%']).all()

    # Check if 'Included in alternate question' is correctly set
    assert (data_engineering.data['Included in alternate question'] == [True, False, False]).all()
