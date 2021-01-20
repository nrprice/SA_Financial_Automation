import shopify
from API_AUTH import API_shopify, PW_shopify
import requests
import pandas as pd

order_dict = {499380322368: {'name': '#1001', 'total': '24.99', 'country': 'United States', 'date': '2018-06-03'}}
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

df = pd.DataFrame.from_dict(order_dict, orient='index').set_index('name')
df.to_excel('shopify_automated_sales_data.xlsx')

























exit()
page_info = ''
order_info = {}
order_json = 1

# Intial request for the first JSon
order_request = requests.get(f'https://{API_shopify}:{PW_shopify}@standing-acrobatics.myshopify.com/admin/api/2021-01/orders.json?limit=100&status=any')

# Order_request.json() returns a json file that gets read in as a dictionary, with the first key being 'orders' which contains all 100 of the orders in that json
order_json = order_request.json()['orders']

while len (order_json) > 1:



    # Attempt at pagination, but found an alternative. Below variables gave access to the subsequent 'page_info' url for the next page.
    # headers = order_request.headers['Link']
    # page_info_index = [headers.find('page_info'), headers.find('>; rel="next"')]
    # page_info = headers[page_info_index[0]:page_info_index[1]][10:]


    print (len(order_json))
    # Finds the last order in the current request and stores the value in last_order_id ready to be passed the next time we search
    last_order_id = order_json[-1]['id']

    # For loop to access each individual order within order_json and pull out only the specific key / values I am interested in
    for order in order_json:

        order_info.update({order['name']:
                               {'total_price': order['total_price'],
                                'date': order['created_at'][:10],
                                'country': order['billing_address']['country']}})

    #  This is when we need to make the second request for the next round of orders.
    # From what I've read it seems you can do this using the last order ID present in the first 100 results, and just carry on like that until you get an error.
    # This works and returns new values.
    order_request = requests.get(f'https://{API_shopify}:{PW_shopify}@standing-acrobatics.myshopify.com/admin/api/2021-01/orders.json?limit=100&status=any&since_id={last_order_id}')

    print (len(order_request.json()['orders']))

shopify.ShopifyResource.clear_session()
