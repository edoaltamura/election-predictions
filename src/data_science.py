from .data_engineering import read_csv, DataEngineering

df = read_csv(DataEngineering().clean_data_file)
print(df.dtypes)

