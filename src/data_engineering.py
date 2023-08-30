import os
import pandas as pd
from typing import Optional

from .configuration import cfg_paths
from .pipeline import measure, development

URL = "https://cdn-dev.economistdatateam.com/jobs/pds/code-test/index.html"


class DataEngineering:

    def __init__(self, url: str = URL, path: Optional[str] = None, filename: str = "dataland_polling.csv",
                 reset: bool = False) -> None:
        self.url = url
        self.path = path
        self.filename = filename

        # Initialise empty dataframe
        self.data = pd.DataFrame()

        self.raw_data_file = os.path.join(cfg_paths.data.raw, self.filename)
        if not os.path.exists(self.raw_data_file) or reset:
            self.load_from_url()

        self.clean_data_file = os.path.join(cfg_paths.data.interim, self.filename)
        if not os.path.exists(self.clean_data_file) or reset:
            self.clean_data()

    @measure
    def load_from_url(self) -> pd.DataFrame:
        self.data = pd.read_html(self.url)[0]
        self.data.to_csv(self.raw_data_file, index=False, na_rep='NaN', mode='w', sep=',')
        return self.data

    def load_from_file(self) -> pd.DataFrame:
        self.data = self.read_csv(self.clean_data_file)
        return self.data

    @staticmethod
    def to_csv(df: pd.DataFrame, path: str) -> None:
        """
        Overload the Pandas method to write dtypes explicitly.
        Save Pandas dataframe to CSV. In addition ir preserves the dypes.
        Prepend dtypes to the top of df (from https://stackoverflow.com/a/43408736/7607701)
        :param df: Input dataframe
        :param path: Output file path.
        :return: None
        """
        df.loc[-1] = df.dtypes
        df.index = df.index + 1
        df.sort_index(inplace=True)

        # Then save it to a csv
        df.to_csv(path, index=False)

    @staticmethod
    def read_csv(path: str) -> pd.DataFrame:
        """
        Overload the Pandas method to read and allocate dtypes explicitly.
        Read types first line of csv and returns the full DataFrame.
        :param path: Input file path.
        :return: DataFrame
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
        return pd.read_csv(path, parse_dates=parse_dates, dtype=dtypes, skiprows=[1])

    @development
    def clean_data(self) -> None:

        if self.data.empty:
            self.data = pd.read_csv(self.raw_data_file)

        # Create a new column with True for rows containing '*' and False otherwise
        self.data['Excludes overseas territories'] = self.data['Sample'].str.contains('\*', regex=True)
        self.data['Sample'] = self.data['Sample'].str.replace('\*', '', regex=True).str.replace(',', '')
        self.data['Sample'] = pd.to_numeric(self.data['Sample'], errors='coerce', downcast='integer')

        self.data['Included in alternate question'] = self.data['Chettam'].str.contains('\*\*', regex=True)
        self.data['Included in alternate question'].fillna(False, inplace=True)
        self.data['Chettam'] = self.data['Chettam'].str.replace('\*\*', '', regex=True).str.rstrip('%')
        self.data['Chettam'] = pd.to_numeric(self.data['Chettam'], errors='coerce', downcast='float') / 100.0

        # Convert percentage signs into fractions
        for col in ['Bulstrode', 'Lydgate', 'Vincy', 'Casaubon', 'Others']:
            self.data[col] = self.data[col].str.rstrip('%').astype('float') / 100.0
            # TODO: Some rows are badly formatted and don't have % sign. They are find though.
            # Maybe write a detection algorithm and print a message.

        self.data['Date'] = pd.to_datetime(self.data['Date'], format='%m/%d/%y')
        self.data['Pollster'] = self.data['Pollster'].apply(str)

        # Account for double counts
        last = self.data[self.data.duplicated(subset=['Date', 'Pollster', 'Sample'], keep='first')]
        assert last['Included in alternate question'].all()

        first = self.data[self.data.duplicated(subset=['Date', 'Pollster', 'Sample'], keep='last')]
        last.index = first.index
        last.loc[first.index, 'Chettam'] = first['Chettam']

        self.data.loc[last.index] = last
        del first, last

        self.data.reset_index(drop=True, inplace=True)
        self.data.drop(['Included in alternate question'], inplace=True, axis=1)

        # Sort by date and group by pollster
        self.data.sort_values(['Pollster', 'Date'], ignore_index=True, inplace=True)
        self.data.reset_index(drop=True, inplace=True)

        self.to_csv(self.data, self.clean_data_file)

    def split_pollsters(self):
        pass

    def regularise_times(self):
        # Interpolate time series for each pollster
        self.data.index = self.data['Date']
        self.data = self.data.resample('12h').interpolate().resample('D').asfreq().dropna()