import os
import pandas as pd

from configuration import path_raw, path_interim


def to_csv(df, path):
    # Prepend dtypes to the top of df (from https://stackoverflow.com/a/43408736/7607701)
    df.loc[-1] = df.dtypes
    df.index = df.index + 1
    df.sort_index(inplace=True)

    # Then save it to a csv
    df.to_csv(path, index=False)


def read_csv(path):
    # Read types first line of csv

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


raw_data_file = f'../{path_raw:s}/dataland_polling.csv'

if not os.path.exists(raw_data_file):
    url = "https://cdn-dev.economistdatateam.com/jobs/pds/code-test/index.html"
    all_tables = pd.read_html(url)[0]
    all_tables.to_csv(raw_data_file, index=False, na_rep='NaN', mode='w', sep=',')

clean_data_file = f'../{path_interim:s}/dataland_polling.csv'

if os.path.exists(clean_data_file):

    df = pd.read_csv(raw_data_file)

    # Create a new column with True for rows containing '*' and False otherwise
    df['Excludes overseas territories'] = df['Sample'].str.contains('\*', regex=True)
    df['Sample'] = pd.to_numeric(df['Sample'].str.replace('\*', '', regex=True).str.replace(',', ''), errors='coerce',
                                 downcast='integer')

    df['Included in alternate question'] = df['Chettam'].str.contains('\*\*', regex=True).fillna(False)
    df['Chettam'] = df['Chettam'].str.replace('\*\*', '', regex=True).str.rstrip('%')
    df['Chettam'] = pd.to_numeric(df['Chettam'], errors='coerce', downcast='float') / 100.0

    # Convert percentage signs
    for col in ['Bulstrode', 'Lydgate', 'Vincy', 'Casaubon', 'Others']:
        df[col] = df[col].str.rstrip('%').astype('float') / 100.0

    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%y')
    df['Pollster'] = df['Pollster'].apply(str)

    # Sort by date and group by pollster
    df.sort_values(['Date', 'Pollster'], ignore_index=True, inplace=True)
    df.reset_index(drop=True, inplace=True)

    to_csv(df, f'../{path_interim:s}/dataland_polling.csv')


df = read_csv(clean_data_file)
print(df.dtypes)
