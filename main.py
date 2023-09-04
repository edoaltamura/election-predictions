# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def main():
    import sys
    sys.path.append('..')

    from src import DataEngineering, DataScience

    de = DataEngineering()
    de.clean_data()
    df = de.load_from_file()
    ds = DataScience(df)
    ds.split_pollsters(resample=True)
    dfs = ds.compute_polling_averages()
    print(dfs)
    ds.dump_results(dfs)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
