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

api_key = ''
api_secret = ''

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
    'side': 'buy'
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