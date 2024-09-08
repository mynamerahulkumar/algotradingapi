# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 20:57:49 2024

@author: LENOVO
"""

import requests
# Fetch products
response = requests.get('https://cdn.india.deltaex.org/v2/products')
products = response.json()

# Fetch ticker information for a specific symbol
symbol = "BTCUSD"  # Example symbol
response = requests.get("https://cdn.india.deltaex.org/v2/tickers" + f"/{symbol}")
ticker_info = response.json()
print(ticker_info)