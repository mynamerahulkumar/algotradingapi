# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 15:27:28 2024

@author: LENOVO
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 15:24:16 2024

@author: LENOVO
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 20:12:09 2024

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

update_data={
  "id": 0,
  "product_id": 27,
  "limit_price": "57000",
  "size": 3,
  "mmp": "disabled",
  "post_only": "false"
}

body = json.dumps(update_data, separators=(',', ':'))
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
response = requests.put('https://cdn.india.deltaex.org/v2/orders', headers=headers, data=body)
order_response = response.json()
print(order_response)
