import shopify
from API_AUTH import API_shopify, PW_shopify
import requests
import pandas as pd
from datetime import datetime

# ID of the first order. Taken from manually downloaded spreadsheet of orders
first_id = 499380322368
# Request to get the information from the first order in first_order_request, converts to JSON dictionary for first_order
first_order_request =  requests.get(f'https://{API_shopify}:{PW_shopify}@standing-acrobatics.myshopify.com/admin/api/2021-01/orders/{first_id}.json?')
first_order = first_order_request.json()['order']

# Instantiation of order_dict
order_dict = {first_order['id']: {'name': first_order['name'],
                             'total': first_order['total_price'],
                             'country': first_order['billing_address']['country'],
                             'date': first_order['created_at'],
                             'shipping_paid': first_order['total_shipping_price_set']['shop_money']['amount']}}


# First ID sanitation - checks it's a number
if type(first_id) != int:
    print ('First ID is not an integer and cannot be used as the order id')
    exit()

# Check to ensure the returned first_order is the correct order. All shopify stores start orders from #1001
try:
    if order_dict[first_id]['name'] == '#1001':
        pass
except:
    print (KeyError)
    print ("First order request has not retrieved the correct ID and the order found is not the first order")
    exit()

# Manual request to find the most recent order id - used for the exit condition of the recursion
# Orders are returned newest to oldest, so the first one returned should always be the latest order
latest_order_request = requests.get(f'https://{API_shopify}:{PW_shopify}@standing-acrobatics.myshopify.com/admin/api/2021-01/orders.json?limit=10&status=any')
latest_id = latest_order_request.json()['orders'][0]['id']

def get_orders(first_id, latest_id, order_dict, output_process=False):

    # Ensures whatever is passed first is passed throughout the recursion
    output_process = output_process

    # When the final ID matches the latest_id requested earlier, the recursion will stop
    # Is checking the last entry on the list of the keys from the order_dict
    while list(order_dict.keys())[-1] != latest_id:

        # Login and open a session with a private auth key
        session = shopify.Session('https://standing-acrobatics.com', '2021-01', PW_shopify)
        shopify.ShopifyResource.activate_session(session)

        # Checks to see that the request actually returns orders.
        if len (shopify.Order.find(status='any', limit=250, since_id=first_id)) == 0:
            print ('no orders found')
            exit()

        # Loop through the returned orders and appends them to the order_dict dictionary
        for order in shopify.Order.find(status='any', limit=250, since_id=first_id):
            order_dict.update({order.id: {'name': order.name,
                                          'total': order.total_price,
                                          'country': order.billing_address.country,
                                          'date': order.created_at[:10],
                                          'shipping_paid': order.total_shipping_price_set.shop_money.amount}})

        # Takes the latest order found and stores it as first_id to be passed back in
        first_id = list (order_dict.keys())[-1]

        # Close the Shopify Session
        shopify.ShopifyResource.clear_session()

        # If output process paramater is True, will print order_dict. Useful to see what's happening in each stage of the recursion.
        if output_process:
            print (order_dict)
            print (f"order_dict contains {len(order_dict)} orders")

        # Passes the new first_id, same latest_id, new updted order_dict and same output_process back and runs function again
        return get_orders(first_id, latest_id, order_dict, output_process)

    # Outputs total number of orders found.
    if output_process:
        print (f"{len(order_dict)} orders found.")
        print (f'Most recent order found is {order_dict[latest_id]}')

    # Once the latest ID in order_dict matches the latest_id variable will exit the recursion
    # Will create a DataFrame from order_dict and save it to Excel.
    df = pd.DataFrame.from_dict(order_dict, orient='index').set_index('name')
    if len(df) == 0:
        print ("No orders have been found or appended.")
        exit()


    # Input to choose whether or not to overwrite.
    # Uses datetime.now() to ensure that data would never be overwritten unless explicitly requested.
    print ('Enter Y to overwrite old spreadsheet, or any other key to save a version of the spreadsheet.')
    answer = input('Overwrite old spreadsheet?')

    # Local path to save spreadsheets
    path = '/Users/nathanprice/Dropbox/Python/SA_Financial_Automation/SA_Financial_Automation/Spreadsheets/'

    # Depending on user answer will either overwrite preexisting
    # or save a unique spreadsheet using the current date + time as a unique key
    if answer.lower() == "y":
        df.to_excel(f'{path}shopify_automated_sales_data.xlsx')
    else:
        current_date = datetime.now()
        df.to_excel(f'{path}shopify_automated_sales_data_{current_date}.xlsx')

    return df


sales_data_df = get_orders(first_id, latest_id, order_dict, output_process=True)

