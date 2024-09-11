# -*- coding: utf-8 -*-
"""
Angel One - Option data streaming

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

from smartapi import SmartConnect
from smartapi.smartWebSocketV2 import SmartWebSocketV2
import os
import urllib
import json
import numpy as np
import pandas as pd
import datetime as dt
from pyotp import TOTP

key_path = r"D:\OneDrive\Udemy\Angel One API"
os.chdir(key_path)

key_secret = open("key.txt","r").read().split()

obj=SmartConnect(api_key=key_secret[0])
data = obj.generateSession(key_secret[2],key_secret[3],TOTP(key_secret[4]).now())

instrument_url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response = urllib.request.urlopen(instrument_url)
instrument_list = json.loads(response.read())

#function to extract all option contracts for a given ticker        
def option_contracts(ticker, option_type="CE", exchange="NFO"):
    option_contracts = []
    for instrument in instrument_list:
        if instrument["name"]==ticker and instrument["instrumenttype"] in ["OPTSTK","OPTIDX"] and instrument["symbol"][-2:]==option_type:
            option_contracts.append(instrument)
    return pd.DataFrame(option_contracts)

#function to extract the closest expiring option contracts
def option_contracts_closest(ticker, duration = 0, option_type="CE", exchange="NFO"):
    #duration = 0 means the closest expiry, 1 means the next closest and so on
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) - dt.datetime.now()).dt.days
    min_day_count = np.sort(df_opt_contracts["time_to_expiry"].unique())[duration]
    
    return (df_opt_contracts[df_opt_contracts["time_to_expiry"] == min_day_count]).reset_index(drop=True)

def option_contracts_atm(ticker, underlying_price, duration = 0, option_type="CE", exchange="NFO"):
    df_opt_contracts = option_contracts_closest(ticker,duration)
    return df_opt_contracts.iloc[abs(pd.to_numeric(df_opt_contracts["strike"])/100 - underlying_price).argmin()]

#nderlying price
underlying_price = obj.ltpData("NSE", "BANKNIFTY-EQ", "26009")["data"]["ltp"]

atm_contract = option_contracts_atm("BANKNIFTY", underlying_price, duration = 1)

#streaming real time data
feed_token = obj.getfeedToken()
sws = SmartWebSocketV2(data["data"]["jwtToken"], key_secret[0], key_secret[2], feed_token)

tokens = [atm_contract["token"]]
correlation_id = "stream_1" #any string value which will help identify the specific streaming in case of concurrent streaming
action = 1 #1 subscribe, 0 unsubscribe
mode = 3 #1 for LTP, 2 for Quote and 3 for SnapQuote

token_list = [{"exchangeType": 2, "tokens": tokens}]


def on_data(wsapp, message):
    print("Ticks: {}".format(message))


def on_open(wsapp):
    print("on open")
    sws.subscribe(correlation_id, mode, token_list)


def on_error(wsapp, error):
    print(error)


# Assign the callbacks.
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error


sws.connect()




