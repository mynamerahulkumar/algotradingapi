# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect - Streaming option data (multithreaded)

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import os
import datetime as dt
import numpy as np
import pandas as pd

cwd = os.chdir("D:\\OneDrive\\Udemy\\Zerodha KiteConnect API\\1_account_authorization")

#generate trading session
access_token = open("access_token.txt",'r').read()
key_secret = open("api_key.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)

#get dump of all NFO instruments
instrument_list = kite.instruments("NFO")

def option_contracts(ticker, option_type="CE", exchange="NFO"):
    option_contracts = []
    for instrument in instrument_list:
        if instrument["name"]==ticker and instrument["instrument_type"]==option_type:
            option_contracts.append(instrument)
    return pd.DataFrame(option_contracts)

#function to extract the closest expiring option contracts
def option_contracts_closest(ticker="BANKNIFTY", duration = 0, option_type="CE"):
    #duration = 0 means the closest expiry, 1 means the next closest and so on
    df_opt_contracts = option_contracts(ticker, option_type)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) - dt.datetime.now()).dt.days
    min_day_count = np.sort(df_opt_contracts["time_to_expiry"].unique())[duration]
    
    return (df_opt_contracts[df_opt_contracts["time_to_expiry"] == min_day_count]).reset_index(drop=True)

#function to extract the atm option contract
def option_contracts_atm(ticker, underlying_price, duration = 0, option_type="CE"):
    df_opt_contracts = option_contracts_closest(ticker,duration,option_type)
    return df_opt_contracts.iloc[abs(df_opt_contracts["strike"] - underlying_price).argmin()]

#nderlying price
underlying_price = kite.quote("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]

atm_contract = option_contracts_atm("BANKNIFTY",underlying_price, duration=1, option_type="CE")

# Initialise
kws = KiteTicker(key_secret[0], kite.access_token)
tokens = [int(atm_contract["instrument_token"])]
option_data = {atm_contract["instrument_token"]:None}

def on_ticks(ws, ticks):
    # Callback to receive ticks.
    option_data[ticks[0]['instrument_token']] = ticks[0]['last_price']

def on_connect(ws, response):
    # Callback on successful connect.
    ws.subscribe(tokens)
    ws.set_mode(ws.MODE_FULL, tokens)

def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.connect(threaded=True) #multithreaded application
