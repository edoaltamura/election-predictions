# Elections trends & forecast
[![Python version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://pypi.org/project/swiftzoom/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/edoaltamura/swiftzoom/blob/main/LICENSE.md)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/7801/badge)](https://www.bestpractices.dev/projects/7801)

A Python framework for analysing current trends and predicting election outcomes from polling data.

![Test image](reports/test.png)

## Get the code
You can download the code by cloning:
```commandline
git clone https://github.com/edoaltamura/election-predictions.git
```

## Run the pipeline
A demo version of the pipeline can be run via the `main.py` file. On Unix-based systems (and subsystems), you can type
```shell
python3 main.py
```
On Windows-based systems, you can type
```commandline
python main.py
```

## Features and FAQs

#### Some days have no polls, some have multiple
For each pollster, days without polls are interpolated if bracketed by days with polls. If different pollsters have provided answers on the same day, these data are considered separately when splitting by pollster. If the same pollster gave two answers on the same day (eg 'University of Bellville-sur-Mer'), then the most recent data is considered.

#### Some pollsters do not include line items for all candidates
The missing candidates are assigned a zero weighting in the weighted average calculation. If one pollster gave two answers on the same day, one of which contains the missing information, then the entries are joined (`SQL UNION OUTER`). A related question, which would be instrumental for probing pollster bias would be "**Why** did a pollster not include line items for all candidates?" 

#### Some pollsters will conduct multiple polls with 'hypotheticals' (eg what if this candidate dropped out?)
This case could manifest itself as the pollster excluding a candidate from the survey, and consequently not providing data for that candidate. To detect and account for this case, more information about the pollster's decisions is required. 

#### The order of candidates on the page may change
The schema assumes a data warehouse, where the order is consistent. Given the current information, it is not possible to reliably determine whether the order of candidates was swapped. An estimate could be made by detecting outliers from the trend, however, this technique gives outcomes which are degenerate with a sudden change of political opinions. 

For a datalake-like schema, additional features can guarantee that the data warehouse layer is consistent. This feature may be introduced with bindings to [schema](https://github.com/keleshev/schema).

#### Formatting may be inconsistent
This behaviour is detected and accounted for by the `DataEngineering.clean_data()` method. Lines which are badly formatted (eg missing `%`) are regularised to the rest of the document. Informative messages are also printed to `sys.stdout`.

#### Opinions can shift suddenly
A rolling average (as in `data/03_final/trends.csv`) cannot promptly capture time-variation features happening quicker than the smoothing time-scale. For this reason, it is useful to consider then raw weighted average of the polling results without any smoothing, as reported in `data/03_final/polling_averages.csv`. This distribution is noisier, but is robust at capturing quick variations in public opinion.

#### A candidate might drop out or join the race late
Drop-outs up to two weeks are interpolated, provided that the candidate rejoins, and their electoral campaign contemplated by pollsters.
If a candidate joins late or drops out early, we assign zero weight to the dates where pollsters provided no data about the candidate. If a candidate drops out without intention of re-joining the run, then additional information is required (eg public announcement). In this case, the time-series can simply be truncated and the polling fractions re-normalised with the remaining candidates.  

#### There may be big gaps in the polling record (for example, around Christmas or for this country’s two-week public holiday in June)
Without additional information of opinion shifts during this time, we can assume that opinions remain stationary, or vary smoothly. In the current implementation, the polling values during gaps of up to two weeks are interpolated. In the future, we will integrate a public-holiday list that enables multi-week interpolation only for public holidays, and not for instance when a candidate drops out and joins again (unless it coincides with a public holiday). 

#### There may be significant data entry errors
The `DataEngineering` class can promptly be extended with additional features that detect, optimise and resolve errors which are discovered during the data exploration phases. Some errors, such as logging, should be addressed in the future data lake schema, while programmatic cleaning should be implemented in the `src/data_engineering.py` submodule.

#### Notes might be attached to specific polls or numbers
This behaviour is detected and accounted for by the `DataEngineering.clean_data()` method. Lines which contain special indicators (eg `*`) are flagged with a `bool` value. The boolean information is then appended onto a new column for further processing.

## Set up
### By creating a virtual environment
Assuming you have installed `venv` and `virtualenv` and have an up-to-date version of `pip` (see [instructions](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)), you can follow this two-step guide to set up this Python library and get it up and running in your system. The election-prediction code was developed to be compatible across all platform, however we will assume the Windows-native `python` run command in what follows, rather than the Unix-native `python3`.
- Create a virtual environment for this project, and activate it.
```commandline
python -m venv env
.\env\Scripts\activate
```
- Install the required packages.
```commandline
python3 -m pip install -r requirements.txt
```
Now the code should be ready to run within the virtual environment. To exit the virtual environment, you can run the command:
```commandline
deactivate
```

### Via PyCharm
Under the menu __Git | VCS__, click on __Clone...__ and enter the GitHub link to this repository. PyCharm can automatically detect the `requirements.txt` file and prompt the installation of the packages within it. We recommend selecting the creation of a project-specific virtual environment.

**Development:** If you plan to introduce new packages or libraries, we recommend using the __Tools__ menu > __Sync Python Requirements__ feature to update the `requirements.txt` file programmatically.

### Via `setup.py` (beta)
This feature is currently under testing, and we recommend setting up the repository via the methods above. 

After cloning the repository to a local host, enter the `election-predictions` directory
- `dir election-predictions` on Windows
- `cd election-predictions` on Unix systems

and run
```commandline
pip install . 
```
`pip` will use `setup.py` to install this module, without needed to call `setup.py` explicitly.


**Note:** You should exclude your virtual environment directory from your version control system using `.gitignore` or similar.

## Graphic design

The layout attempts to match the style of the plots in _The Economist_ 's [Graphic detail](https://www.economist.com/graphic-detail?utm_medium=cpc.adword.pd&utm_source=google&ppccampaignID=18151738051&ppcadID=&utm_campaign=a.22brand_pmax&utm_content=conversion.direct-response.anonymous&gclid=Cj0KCQjwgNanBhDUARIsAAeIcAvIXMRR0ecYNG1wFTmK1J8uDBE1V-EE7ic7LtNSwpX3vn8ITqD58BsaAiu3EALw_wcB&gclsrc=aw.ds) using `matplotlib` style sheets and dynamic aspect ratio scaling. Find out more in the Matplotlib stylesheet at `src/mplstyles/economist_xyplot.mplstyle` and the `src/visualisation.py` submodule.

Example usage:
```python
import pandas as pd
import matplotlib.pyplot as plt
from src import PlotTimeSeries  # Import the PlotTimeSeries class

# Create a sample DataFrame (replace this with your own data)
data = {
    'Date': pd.date_range(start='2023-01-01', periods=365),
    'Bulstrode': [0.1 * i for i in range(365)],
    'Lydgate': [0.15 * i for i in range(365)],
    'Vincy': [0.08 * i for i in range(365)],
}

df = pd.DataFrame(data)

# Create an instance of PlotTimeSeries
plt_ts = PlotTimeSeries()

# Get the figure and axes objects
fig, ax = plt_ts.get_panels()

# Plot the data for each candidate
for candidate in ['Bulstrode', 'Lydgate', 'Vincy']:
    ax.plot(df['Date'], df[candidate], label=candidate)

# Set titles and labels
plt_ts.set_title('Candidate Polling Trends', subtitle='Fraction of candidate polling, %/100')
plt_ts.set_source('Dataland political archive 2023', pad=0.15)

# Add a legend
ax.legend(fontsize=10, loc='upper left', frameon=True, framealpha=0.85)

# Save the plot
plt_ts.savefig('my_awesome_economist_figure.png', dpi=300)

# Show the plot (if you want to display it)
plt.show()
```

## Expected output from `main.py`
```commandline
$ python main.py

⏱ | Calling load_from_url()
⏱ | Done: load_from_url() took 0.3231 sec
Found 22 badly formatted rows in column 'Bulstrode':
Found 22 badly formatted rows in column 'Lydgate':
Found 90 badly formatted rows in column 'Chettam':
Found 51 badly formatted rows in column 'Vincy':
Found 38 badly formatted rows in column 'Casaubon':
Found 22 badly formatted rows in column 'Others':
Some pollsters have given multiple responses:
	['University of Bellville-sur-Mer']
Considering only the most recent information:
	[Timestamp('2024-03-22 00:00:00'), Timestamp('2024-02-23 00:00:00'), Timestamp('2024-01-26 00:00:00')]
Dropping rows: {first.index}

A glimpse of the clean data:
         Date          Pollster  ...  Others  Excludes overseas candidates
0 2023-10-12  Bardi University  ...   0.171                         False
1 2023-10-18  Bardi University  ...   0.078                         False
2 2023-10-24  Bardi University  ...   0.074                         False
3 2023-10-30  Bardi University  ...   0.083                         False
4 2023-11-05  Bardi University  ...   0.155                         False
5 2023-11-11  Bardi University  ...   0.112                         False
6 2023-11-17  Bardi University  ...   0.099                         False
7 2023-11-23  Bardi University  ...   0.091                         False
8 2023-11-29  Bardi University  ...   0.141                         False
9 2023-12-05  Bardi University  ...   0.115                         False

[10 rows x 10 columns]
Splitting 'Verity Insights': 100%|██████████| 11/11 [00:00<00:00, 89.56it/s]
Candidate average for 'Bulstrode':   0%|          | 0/6 [00:00<?, ?it/s]<local-hot-directory>\election-predictions\src\data_science.py:284: RuntimeWarning: 
Pollster 'Calvo Group' only gave 1 reports. This behaviour is accounted for in the weighted averages, but you should investigate this pollster's data further.
  warn(
Candidate average for 'Lydgate':  17%|█▋        | 1/6 [00:00<00:03,  1.36it/s]  <local-hot-directory>\election-predictions\src\data_science.py:284: RuntimeWarning: 
Pollster 'Calvo Group' only gave 1 reports. This behaviour is accounted for in the weighted averages, but you should investigate this pollster's data further.
  warn(
Candidate average for 'Vincy':  17%|█▋        | 1/6 [00:00<00:03,  1.36it/s]  <local-hot-directory>\election-predictions\src\data_science.py:284: RuntimeWarning: 
Pollster 'Calvo Group' only gave 1 reports. This behaviour is accounted for in the weighted averages, but you should investigate this pollster's data further.
  warn(
Candidate average for 'Casaubon':  50%|█████     | 3/6 [00:00<00:00,  3.97it/s]<local-hot-directory>\election-predictions\src\data_science.py:284: RuntimeWarning: 
Pollster 'Calvo Group' only gave 1 reports. This behaviour is accounted for in the weighted averages, but you should investigate this pollster's data further.
  warn(
Candidate average for 'Chettam':  50%|█████     | 3/6 [00:00<00:00,  3.97it/s] <local-hot-directory>\election-predictions\src\data_science.py:284: RuntimeWarning: 
Pollster 'Calvo Group' only gave 1 reports. This behaviour is accounted for in the weighted averages, but you should investigate this pollster's data further.
  warn(
Candidate average for 'Others':  83%|████████▎ | 5/6 [00:01<00:00,  5.86it/s] <local-hot-directory>\election-predictions\src\data_science.py:284: RuntimeWarning: 
Pollster 'Calvo Group' only gave 1 reports. This behaviour is accounted for in the weighted averages, but you should investigate this pollster's data further.
  warn(
Candidate average for 'Others': 100%|██████████| 6/6 [00:01<00:00,  5.14it/s]
Writing dataset 'polling_averages.csv' to: > <local-hot-directory>\election-predictions\data\03_final\polling_averages.csv
Writing dataset 'trends.csv' to: > <local-hot-directory>\election-predictions\data\03_final\trends.csv
Figure test.png saved in reports directory.
```

## Cite this software
You can print an up-to-date `bibtex` citation handle via:
```python
from src import __cite__

print( __cite__ )
```
This code dynamically allocates the current version of the code being uses and the date of the latest update, as given by the latest Git commit in the Git history.

A template of the citation handle is illustrated below:
```text
@software{altamura_elections
          author = {{Altamura}, Edoardo},
          title = {"An statistical machine learning framework for election predictions"}
          url = {https://github.com/edoaltamura/election-predictions}
          version = {__version__}
          date = {__date_last_update__}
}
```

## Licence
```text
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```