import os
import pandas as pd
from typing import Optional
from tqdm.auto import tqdm

from .io import IO
from .configuration import cfg_paths
from .pipeline import measure, development


class DataScience(IO):

    def __init__(self, df: pd.DataFrame, split_basename: str = 'pollster_split') -> None:
        super().__init__()
        self.data = df
        self.split_basename = split_basename

    def split_pollsters(self):

        # First get the unique names of pollsters
        unique_pollsters = self.data['Pollster'].unique()
        for pollster in (pbar := tqdm(unique_pollsters)):

            # Dynamically display the pollster being searched
            pbar.set_description(f"Splitting '{pollster:s}'")

            # Get the subset corresponding to a particular pollster
            pollster_split = self.data.loc[self.data['Pollster'] == pollster]

            # Save it to interim data directory
            self.to_csv(pollster_split, self.get_split_file_path(pollster))

    def get_split_file_path(self, pollster: str) -> str:

        _pollster_join_name = '-'.join(pollster.split())
        _pollster_join_name = f"{self.split_basename:s}_{_pollster_join_name:s}.csv"

        return os.path.join(cfg_paths.data.interim, _pollster_join_name)

    # @development
    # @measure
    def regularise_time(self, pollster: str):

        file_path = self.get_split_file_path(pollster)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File for pollster '{pollster:s}' not found in the interim data directory. Check "
                                    "that the interim directory is correctly configured, or check that the "
                                    "`DataScience.split_pollsters()` function was called.")

        pollster_data = self.read_csv(file_path)
        pollster_data.index = pd.to_datetime(pollster_data.index)
        res = pollster_data.resample('6h').interpolate().resample('24h').asfreq()
        print(res.head())





