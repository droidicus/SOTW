# SOTW
Accounting and data analytics for SOTW

# Installation
## Requirements
* Python 3.10: https://www.python.org/
* Pip (should be included in the installer or available in the distro packages)
* pipenv: `pip install pipenv`

## Installation
* Clone repo
* Open terminal in repo directory
* Run: `pipenv install`
* NOTE: If you want the development dependencies to be installed as well run this instead: `pipenv install --dev`

# Use
## Preparation
Download at least 1 full week of bank data that includes the Fri-Fri time period you want to analyze. More is fine, less is bad. Put CSV file in the repo directory.

## Help
Execute the following to get the build-in help:

`pipenv run python calc_pay.py --help`

## Execution
From the repo directory execute the following command to use the file `sotw.csv`, a 30% commission rate, and for the week ending April 20th, 2022 at midnight UTC (NOTE: the file and rate shown are the default values if not provided, if the date is not provided than the most recent Friday is used as the end_date):

`pipenv run python calc_pay.py --file sotw.csv --rate 0.3 --end_date 2022-04-20`

To accept the defaults and run the file `sotw.csv` from the most recent Friday at midnight to 2 Friday's ago at midnight:

`pipenv run python calc_pay.py`

The option `--quiet` can also be used to reduce the information provided:

`pipenv run python calc_pay.py --quiet --all`

The Option `--weeks` allows more than one week of data to be sliced, and if the value given is -1 it uses all data in the CSV file.

`pipenv run python calc_pay.py --weeks -1`

The option `--plot` enables plotting several different graphs from the data, the results are `*.png` files within the execution directory.

`pipenv run python calc_pay.py --plot`

These options can be combined.

# NOTE
ALWAYS make sure the first sale and last sale deltas make sense, if there is more than a short time here it may indicate missing data.
