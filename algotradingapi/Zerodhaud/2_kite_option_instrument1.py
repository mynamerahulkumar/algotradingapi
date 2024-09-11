# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 14:01:52 2024

@author: LENOVO
"""
from kiteconnect import KiteConnect
import pandas as pd
Kite_api_key=''

kite_api_secret=''

# =============================================================================
# https://kite.trade/connect/login?api_key=gk1nt2kv793a8t3n
# =============================================================================
kite_access_token=''

# =============================================================================
#  create a trading session
# =============================================================================
kite=KiteConnect(api_key=Kite_api_key)

kite.set_access_token(kite_access_token)

# =============================================================================
#  get all instruments
# instrumentlist=kite.instruments("NFO")
# =============================================================================
instrumentlist=kite.instruments("NFO")

underlying_price=kite.quote("NSE:NIFTY BANK")
# =============================================================================
# get all option contract
# =============================================================================



