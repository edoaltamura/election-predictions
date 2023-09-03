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
