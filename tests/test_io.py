import pytest
import pandas as pd
import os
import tempfile

from src import io

sample_columns: str = "Date,Pollster,Sample,Bulstrode,Lydgate,Vincy,Casaubon,Chettam,Others,Excludes overseas " \
                      "territories "

sample_dtypes: str = "datetime64[ns],object,int16,float64,float64,float64,float64,float32,float64,bool"

sample_data: str = """2023-10-12 00:00:00,Bardi University,683,0.307,0.405,,0.11699999999999999,,0.171,False
2023-10-18 00:00:00,Bardi University,709,0.32,0.376,,0.141,0.08500000089406967,0.078,False
2023-10-24 00:00:00,Bardi University,706,0.292,0.373,,0.134,0.12700000405311584,0.07400000000000001,False
2023-10-30 00:00:00,Bardi University,669,0.32299999999999995,0.325,,0.161,0.10899999737739563,0.083,False
2023-11-05 00:00:00,Bardi University,650,0.327,0.318,,0.2,,0.155,False"""


# Create a temporary directory for testing
@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_directory:
        yield temp_directory


def test_to_csv_and_read_csv(temp_dir):

    # Recast the col names and dtypes
    _sample_columns = sample_columns.split(',')
    _sample_dtypes = sample_dtypes.split(',')

    # Create a sample DataFrame
    df = pd.DataFrame(sample_data, columns=_sample_columns)
    df = df.astype(dict(zip(_sample_columns, _sample_dtypes)))

    # Specify the path where you want to save the CSV file
    csv_path = os.path.join(temp_dir, 'sample_data.csv')

    # Use the custom to_csv method to save the DataFrame to a CSV file
    custom_io = io.IO()
    custom_io.to_csv(df, csv_path)

    # Now, let's read the CSV file back into a DataFrame to verify the data types preservation
    loaded_df = custom_io.read_csv(csv_path)

    # Check if the loaded DataFrame is equal to the original DataFrame
    assert df.equals(loaded_df)