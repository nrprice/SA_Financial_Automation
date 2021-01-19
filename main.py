from import_and_clean import shopify, chase, paypal
from analysis import report
import pandas as pd
pd.set_option('display.width', 800)
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 100)

"""
The entire reporting can be run from this script. An example is below to create plots for June 2018 to June 2020.
.single_reports will create individual .png files for revenue, profit and costs across the specified period.
.combined_reports will plot each of the above on the same plot.
"""

june_2018_june_2020 = report(start_period=['2018', '06'], end_period=['2020', '08'])
june_2018_june_2020.single_reports()
june_2018_june_2020.combined_report()
