import shopify
from API_AUTH import API_shopify, PW_shopify
import requests
import pandas as pd

### To do list
# Need to validate the input and outputs
# specifically the Json return and the final df to make sure it's != 0


order_dict = {499380322368: {'name': '#1001',
                             'total': '24.99',
                             'country': 'United States',
                             'date': '2018-06-03'}}

first_id = list(order_dict.keys())[0]

# Manual request to find the most recent order id - used for the exit condition of the recursion
order_request = requests.get(f'https://{API_shopify}:{PW_shopify}@standing-acrobatics.myshopify.com/admin/api/2021-01/orders.json?limit=100&status=any')
latest_id = order_request.json()['orders'][0]['id']

def get_orders(first_id, latest_id):

    global order_dict

    while list(order_dict.keys())[-1] != latest_id:
        # Login and open a session with a private auth key
        session = shopify.Session('https://standing-acrobatics.com', '2021-01', PW_shopify)
        shopify.ShopifyResource.activate_session(session)

        for order in shopify.Order.find(status='any', limit=250, since_id=first_id):
            order_dict.update({order.id: {'name': order.name, 'total': order.total_price,'country': order.billing_address.country, 'date': order.created_at[:10]}})

        first_id = list (order_dict.keys())[-1]

        # Close the Shopify Session
        shopify.ShopifyResource.clear_session()
        return get_orders(first_id, latest_id)

get_orders(first_id, latest_id)

if len(order_dict) == 0:
    print ('The dataframe has returned an empty dictionary. Check the inputs.')
    exit()

df = pd.DataFrame.from_dict(order_dict, orient='index').set_index('name')

df.to_excel('shopify_automated_sales_data.xlsx')