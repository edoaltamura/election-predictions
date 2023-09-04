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
from django.core.exceptions import ValidationError

from src import DataEngineering
from src.data_engineering import URL


def validate_url(url: str):
    try:
        DataEngineering().validate_url(url)
        return True
    except ValidationError:
        return False


test_data = [
    ('https://www.google.com/', True),
    ('https://www.googlecom', False),
    ('https://www.google.com>/', False),
    (URL, True)
]


@pytest.mark.parametrize('sample, expected_output', test_data)
def test_validate_url(sample, expected_output):
    assert validate_url(sample) == expected_output


@pytest.fixture
def load_from_url():
    """
    Fixtures are callables decorated with @fixture
    """
    print("(Doing Local Fixture setup stuff!)")
    de = DataEngineering()
    de.load_from_url()
    return de.data, de.url


def test_url_parsing(load_from_url):
    _, url = load_from_url
    assert url == URL


def test_data_instance(load_from_url):
    """
    Fixtures can be invoked simply by having a positional arg
    with the same name as a fixture:
    """
    data, _ = load_from_url
    assert isinstance(data, pd.DataFrame)


def test_data_emptiness(load_from_url):
    """
    Fixtures can be invoked simply by having a positional arg
    with the same name as a fixture:
    """
    data, _ = load_from_url
    assert not data.empty


def test_data_time_col(load_from_url):
    """
    Fixtures can be invoked simply by having a positional arg
    with the same name as a fixture:
    """
    data, _ = load_from_url
    assert 'Date' in data.columns
