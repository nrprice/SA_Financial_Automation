import shopify
from API_AUTH import API_shopify, PW_shopify
import requests
import pandas as pd


session = shopify.Session('https://standing-acrobatics.com', '2021-01', PW_shopify)
shopify.ShopifyResource.activate_session(session)
orders = requests.get(f'https://{API_shopify}:{PW_shopify}@standing-acrobatics.myshopify.com/admin/api/2021-01/orders.json?status=any')
orders = orders.json()['orders']
shopify.ShopifyResource.clear_session()


order_info = {}

for order in orders:

    order_info.update({order['name']:{'total_price': order['total_price'], 'date': order['created_at'][:10], 'country': order['billing_address']['country']}})


df = pd.DataFrame.from_dict(order_info, orient='index')

print (df)