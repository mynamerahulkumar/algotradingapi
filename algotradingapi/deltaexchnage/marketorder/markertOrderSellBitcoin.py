# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 14:10:03 2024

@author: LENOVO
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 21:00:42 2024

@author: LENOVO
"""

import hashlib
import hmac
import json
import time

import requests
token_path = "C:/Users/LENOVO/OneDrive/Documents/A_Udeyme/ppts/Algo_trradiing/configs/deltakeyfile.txt"
key_secret = open(token_path,'r').read().split()
api_key=key_secret[0]
api_secret=key_secret[1]

# Create the signature
def generate_signature(method, endpoint, payload):
    timestamp = str(int(time.time()))
    signature_data = method + timestamp + endpoint + payload
    message = bytes(signature_data, 'utf-8')
    secret = bytes(api_secret, 'utf-8')
    hash = hmac.new(secret, message, hashlib.sha256)
    return hash.hexdigest(), timestamp

# Prepare the order data
order_data = {
    'product_id': 27,  # Product ID for BTCUSD is 27
    'size': 1,
    'order_type': 'market_order',
    'side': 'sell',
    "limit_price": "58050",
    "stop_price": "57100",
    "stop_order_type": "take_profit_order",
    "bracket_stop_loss_limit_price": "58050",
      "bracket_stop_loss_price": "58060",
     "bracket_take_profit_limit_price": "56100",
     "bracket_take_profit_price": "56000",
     "post_only": "true",
     "close_on_trigger": "true",
}

body = json.dumps(order_data, separators=(',', ':'))
method = 'POST'
endpoint = '/v2/orders'
signature, timestamp = generate_signature(method, endpoint, body)
# Add the API key and signature to the request headers
headers = {
    'api-key': api_key,
    'signature': signature,
    'timestamp': timestamp,
    'Content-Type': 'application/json'
}
response = requests.post('https://cdn.india.deltaex.org/v2/orders', headers=headers, data=body)
order_response = response.json()
print(order_response)