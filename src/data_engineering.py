import os
import pandas as pd
from typing import Optional

from .configuration import cfg_paths
from .pipeline import measure, development
from .io import IO

URL = "https://cdn-dev.economistdatateam.com/jobs/pds/code-test/index.html"


class DataEngineering(IO):

    def __init__(self, url: str = URL, path: Optional[str] = None, filename: str = "dataland_polling.csv",
                 reset: bool = False) -> None:
        super().__init__()
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
