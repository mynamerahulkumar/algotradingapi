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


# =============================================================================
# get all option contract
# =============================================================================

def get_option_contracts(ticker,option_type="CE",exchange="NFO"):
    option_contract=[]
    for instrument in instrumentlist:
        if(instrument["name"]==ticker and instrument["instrument_type"]==option_type):
            option_contract.append(instrument)
    return pd.DataFrame(option_contract)

option_contract2=get_option_contracts("BANKNIFTY")
# =============================================================================
# profile=kite.profile()
# =============================================================================
# =============================================================================
# underlying_price=kite.quote("NSE:INFY")

# =============================================================================
