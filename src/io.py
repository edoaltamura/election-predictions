import pandas as pd


class IO:

    def __init__(self) -> None:
        pass

    @staticmethod
    def to_csv(df: pd.DataFrame, path: str) -> None:
        """
        Overload the Pandas method to write dtypes explicitly.
        Save Pandas dataframe to CSV. In addition ir preserves the dypes.
        Prepend dtypes to the top of df (from https://stackoverflow.com/a/43408736/7607701)
        :param df: Input dataframe
        :param path: Output file path.
        :return: None

        Note:
            Prepending dtypes with
            ```python
            df.loc[-1] = df.dtypes
            df.index = df.index + 1
            df.sort_index(inplace=True)
            ```
            Returns a view of the DataFrame instead of a copy, and is now deprecated.
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
