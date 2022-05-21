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
* `pipenv install --dev`

# Use
## Preparation
Download at least 1 full week of bank data that includes the Fri-Fri time period you want to analyze. More is fine, less is bad. Put CSV file in the repo directory.

## Help
Execult the following to get the build-in help:

`pipenv python calc_pay.py --help`

## Execution
From the repo directory execute the following command to use the file `sotw.csv`, a 30% commission rate, and for the week ending April 20th, 2022 (NOTE: the file and rate shown are the default values if not provided, if the date is not provided than the most recently Friday is used as the end_date):

`pipenv python calc_pay.py --file sotw.csv --rate 0.3 --end_date 2022-04-20`

To accept the defaults and run the file `sotw.csv` from the most recent Friday at midnight to 2 Friday's ago at midnight:

`pipenv python calc_pay.py`

## NOTE
ALWAYS make sure the first sale and last sale deltas make sense, if there is more than a short time here it may indicate missing data.
