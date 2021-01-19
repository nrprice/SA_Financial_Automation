from import_and_clean import paypal, chase, shopify, current_month, current_year
import seaborn as sns
sns.set_style("darkgrid")
sns.set_palette('muted')
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import os


# Group each dataframe by month & year and set the year_month as an index

shopify_revenue = shopify.groupby(['year_month'])['total_shopify'].sum().reset_index().set_index('year_month')
paypal_revenue = paypal.groupby(['year_month'])['net'].sum().reset_index().set_index('year_month')
chase_costs = chase.groupby(['year_month'])['amount'].sum().reset_index().set_index('year_month')

# Joins the above groupbys together to create one dataframe and renames the columns
combined = shopify_revenue.join(paypal_revenue).join(chase_costs).rename(columns={'total_shopify': 'shopify_revenue',
                                                                                  'net': 'paypal_revenue',
                                                                                  'amount': 'chase_costs'}).fillna(0)
# Adds total revenue column
combined['total_revenue'] = combined['shopify_revenue'] + combined['paypal_revenue']
# Adds profitcolumn
combined['profit'] = combined['total_revenue'] + combined['chase_costs']
# Set index as a datetimeindex
combined.index = pd.to_datetime(combined.index, format='%Y-%m')

# creates a class to allow for reporting by specifying the start and end period at the instantiation of the class.
class report:
    """The start period and end period should be passed as a list containing two strings [year, month] in the format ['0000', '00']"""
    y_values = ['total_revenue', 'profit', 'chase_costs']
    path = os.getcwd() + '/Plots/'
    def __init__(self, start_period=[current_year, current_month], end_period=None, dataframe=combined):

        start_period = pd.to_datetime(str(start_period[0]) + str(start_period[1]), format="%Y%m")


        if end_period == None:
            self.dataframe = dataframe[dataframe.index == start_period]
        else:
            end_period = pd.to_datetime(str(end_period[0]) + str(end_period[1]), format="%Y%m")
            self.dataframe = dataframe[(dataframe.index >= start_period) & (dataframe.index <= end_period)]

        self.start_period_string = str(start_period)[:10]
        self.end_period_string = str(end_period)[:10]


    def single_reports(self, y_values=y_values, path=path):

        # There is something I'm missing about how to pass variables to a function within a class without using them as arguments in the function.
        import matplotlib.ticker as mtick
        fmt = '${x:,.0f}'
        tick = mtick.StrMethodFormatter(fmt)

        # Seems to be a bug within pandas and using datetimeindexes and this line fixes that
        pd.plotting.register_matplotlib_converters()

        # Plots for each y_val in y_values argument
        for y_val in y_values:
            figure = sns.lineplot(data=self.dataframe, x=self.dataframe.index, y=y_val, marker='o')
            figure.set(title=f'{y_val.replace("_", " ").title()} from {self.start_period_string} to {self.end_period_string}', xlabel='Date', ylabel=(y_val).replace("_", " ").title())
            figure.yaxis.set_major_formatter(tick)
            figure.figure.autofmt_xdate()
            plt.tight_layout()
            figure.figure.savefig(f'{path}{y_val}_{self.start_period_string} to {self.end_period_string}.png'.title())
            plt.clf()

    def combined_report(self, y_values=y_values, path=path):

        # There is something I'm missing about how to pass variables to a function within a class without using them as arguments in the function.
        import matplotlib.ticker as mtick
        fmt = '${x:,.0f}'
        tick = mtick.StrMethodFormatter(fmt)

        # Plots each of the y_vals on the same plot for easy comparison
        figure = self.dataframe[y_values].plot(kind='line', marker='o')
        figure.set(title=f'Revenue, Profit and Costs for {self.start_period_string} to {self.end_period_string}', xlabel='Date', ylabel='Amount')
        figure.yaxis.set_major_formatter(tick)
        figure.figure.autofmt_xdate()
        # The x values are right up against the edges, so I wanted to try and expand the x_lim but this did not work. Might have to manually add a NaN value for the month prior and after.
        # x_lim = figure.axes.get_xlim()
        # figure.axes.set_xlim((x_lim[0] * 1.01, x_lim[1] * 1.01))
        plt.tight_layout()
        figure.figure.savefig(f'{path}rev_prof_costs_{self.start_period_string} to {self.end_period_string}.png'.title())

