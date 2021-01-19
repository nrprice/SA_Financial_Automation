# Import the needed modules
import pandas as pd
from datetime import datetime
import os
import numpy as np
import re

# Sets max view for Pandas rows and columns
pd.set_option('display.width', 800)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 60)
# Retrieve the current month/year as a string
current_month = datetime.now().strftime('%m')
current_year = datetime.now().strftime('%Y')
# Any CSV files in the same folder will be converted to .xlsx format
# and have the current month apended to it's name
# Will not work if the folder already contains an .xlsx file

def year_change(x):
    return pd.to_datetime(x).strftime('%Y')
def month_change(x):
    return pd.to_datetime(x).strftime('%m')
def year_month_change(x):
    return pd.to_datetime(x).strftime('%Y-%m')

path = os.getcwd() + '/Spreadsheets/'

def remove_files():
    for file in os.listdir(path):
        if file.endswith(".xlsx"):
            os.remove(path + file)
def convert_csv_to_excel():
    for file in os.listdir(path):
        if file.endswith(".xlsx"):
            print ('You already have .xlsx files here. Please organise folder')
            exit()
        if file.endswith(".CSV") or file.endswith(".csv"):
            new_file_name = f'{file.replace(".csv", "").replace(".CSV", "")}.xlsx'
            read_file = pd.read_csv(f'{path + file}')
            read_file.to_excel(path+new_file_name, index=False)

            # writer = pd.ExcelWriter(new_file_name)
            # read_file.to_excel(writer, index = False)
            # writer.save()
            print (f'{file} has been saved as {new_file_name}')

chase = path + 'Chase.xlsx'
paypal = path + 'PayPal.xlsx'
shopify = path + 'Shopify.xlsx'

def clean_chase(sheet = chase):
    # Reads spreadsheet in
    chase_df = pd.read_excel(sheet, usecols=['Details', 'Posting Date', 'Description', 'Amount'])
    # Renames the columns because it broke somewhere
    chase_df = chase_df.rename(columns={'Details': 'date', 'Posting Date': 'description', 'Description': 'amount', 'Amount': 'type'})
    # Adds a year_month column to the dataframe containing the year + month
    # chase_df['year'] = chase_df['date'].apply(year_change)
    # chase_df['month'] = chase_df['date'].apply(month_change)
    chase_df['year_month'] = chase_df['date'].apply(year_month_change)
    # Only retains ACH_Debit and DEBIT_CARD information
    chase_df = chase_df[(chase_df['type'] == 'ACH_DEBIT') | (chase_df['type'] == "DEBIT_CARD")]
    # Overwrites the previous excel sheet and Saves the Chase Dataframe
    writer = pd.ExcelWriter(f'{sheet}')
    chase_df.to_excel(writer, index=False)
    writer.save()
    print (f'Your {sheet.split("/")[-1]} sheet was formatted correctly')
    return chase_df


def clean_paypal(sheet = paypal):
    # Reads spreadsheet in
    paypal_df = pd.read_excel(sheet, usecols=['Date', 'Net', 'Type'])
    # formats columns to lower case
    paypal_df.columns = [x.lower() for x in paypal_df.columns]
    # Adds a Year and Month column to the dataframe containing the year + month
    # paypal_df['year'] = paypal_df['date'].apply(year_change)
    # paypal_df['month'] = paypal_df['date'].apply(month_change)
    paypal_df['year_month'] = paypal_df['date'].apply(year_month_change)
    # Casts the 'net' column to an int
    paypal_df['net'] = pd.to_numeric(paypal_df['net'], errors='coerce')
    # Only displays incoming positive subscription payments
    paypal_df = paypal_df[paypal_df['type'] == 'Subscription Payment']
    paypal_df = paypal_df[paypal_df['net'] > 0]
    # Overwrites the previous excel sheet and Saves the PayPal Dataframe
    writer = pd.ExcelWriter(f'{sheet}')
    paypal_df.to_excel(writer, index=False)
    writer.save()
    print (f'Your {sheet.split("/")[-1]} sheet was formatted correctly')
    return paypal_df


def clean_shopify(sheet = shopify):
    # Reads spreadsheet in
    shopify_df = pd.read_excel(sheet, usecols=['Name',
                                               'Paid at',
                                               'Total',
                                               'Lineitem name',
                                               'Shipping',
                                               'Shipping Country',
                                               'Payment Method'])
    #Renames columns to lower case and removes spaces
    shopify_df.columns = [x.strip().replace(" ", "_").lower() for x in shopify_df.columns]
    # Replaces NaN values with a placeholder date / time string
    shopify_df['paid_at'] = shopify_df['paid_at'].fillna("1990-06-01 18:23:07 -0400")
    # Adds a Year and Month column to the dataframe containing the year + month
    shopify_df['year'] = shopify_df['paid_at'].apply(year_change)
    shopify_df['month'] = shopify_df['paid_at'].apply(month_change)
    shopify_df['year_month'] = shopify_df['paid_at'].apply(year_month_change)
    # Creates a net column that takes away the payment processing fees from the totals
    shopify_df['net'] = np.where(shopify_df['payment_method'] == 'Shopify Payments',
                              shopify_df['total'] - ((shopify_df['total'] * 0.026) + .30),
                              shopify_df['total'] - shopify_df['total'] * 0.03)
    # Limits the calculated net to 2 decimal places and restores it as a float
    shopify_df['net'] = shopify_df['net'].apply(lambda x: float("{:.2f}".format(x)))
    # Removes the strange orders that don't have a date - these were all in person sales that I had to hack together in the shopify store so they don't display correctly now. 
    shopify_df = shopify_df[(shopify_df['year'] != '1990')]
    # Sets the order number as the index
    shopify_df = shopify_df.set_index('name')
    # Overwrites the previous excel sheet and Saves the PayPal Dataframe
    writer = pd.ExcelWriter(f'{shopify}')
    shopify_df.to_excel(writer, index=False)
    writer.save()
    print (f'Your {sheet.split("/")[-1]} sheet was formatted correctly')
    return shopify_df


def warehouse_invoice():
    # Define path variable where spreadsheets are stored
    path = os.getcwd() + '/Spreadsheets/Warehouse/'
    # Intiate empty dataframe to be appended to
    shipped_df = pd.DataFrame()
    # Loop through all files in the spreadhseet directory and append any where DATE has a value
    for file in os.listdir(path):
        if file.endswith('.xlsx'):
            temp_df = pd.read_excel(path + file)
            temp_df = temp_df[temp_df['DATE'].notna()]
            shipped_df = shipped_df.append(temp_df)

    # Rename columns to remove spaces, add underscores and make lowercase
    shipped_df.columns = [x.strip().replace(" ", "_").lower() for x in shipped_df.columns]
    # Reset index and remove old index column
    shipped_df = shipped_df.reset_index().drop(columns=['index'])

    # Returned items are an edge case, in which case they do not have a SHIP COST value
    shipped_df = shipped_df[shipped_df['ship_cost'].notna()]

    # Remove unneeded columns
    shipped_df = shipped_df[['order_#', 'total']]

    # Edge cases where I manually set up an order do not follow the #XXXX format, remove those as they will not merge later.

    # regex function to find only rows that match #XXXX format
    def regex_function(x):
        return bool(re.match("^#[0-9]{4}$", x))

    shipped_df = shipped_df[shipped_df['order_#'].apply(regex_function) == True]

    #sets index as the order number
    shipped_df = shipped_df.set_index('order_#')
    return shipped_df

remove_files()
convert_csv_to_excel()
chase = clean_chase()
paypal = clean_paypal()
shopify = clean_shopify()
warehouse = warehouse_invoice()

# Merges the sales data with available shipping cost data
shopify = shopify.join(warehouse, lsuffix='_shopify', rsuffix='_shipping')
shopify['net'] = shopify['net'] - shopify['total_shipping']
shopify.to_excel(path+'shopify_shipping.xlsx')



