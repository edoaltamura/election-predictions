# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def main():
    import sys
    sys.path.append('..')

    from src import DataEngineering, DataScience

    df = DataEngineering().load_from_file()
    DataScience(df).regularise_time('Verity Insights')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
