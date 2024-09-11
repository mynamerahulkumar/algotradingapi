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
import mibian
import pandas as pd
import datetime as dt
import threading
from pyotp import TOTP
import time

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

underlying_price = obj.ltpData("NSE", "BANKNIFTY-EQ", "26009")["data"]["ltp"]

def option_contracts_atm(ticker, underlying_price):
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    df_opt_contracts["strike"] = pd.to_numeric(df_opt_contracts["strike"])/100
    atm_strike = df_opt_contracts.loc[abs(df_opt_contracts["strike"] - underlying_price).argmin(),'strike']    
    return (df_opt_contracts[df_opt_contracts["strike"] == atm_strike]).sort_values(by=["time_to_expiry"]).reset_index(drop=True).iloc[:4,:]
   
opt_chain = option_contracts_atm("BANKNIFTY", underlying_price)
opt_chain["instrument_type"] = opt_chain["symbol"].str[-2:]


tokens = opt_chain["token"].to_list()
symbol_dict = dict(zip(opt_chain.token, opt_chain.symbol))
option_data = {symbol_dict[i]:{} for i in tokens}

for symbol in opt_chain.symbol:
    option_data[symbol]["strike"] = opt_chain.loc[opt_chain.symbol == symbol, "strike"].to_list()[0]
    option_data[symbol]["type"] = opt_chain.loc[opt_chain.symbol == symbol, "instrument_type"].to_list()[0]
    option_data[symbol]["time_to_expiry"] = opt_chain.loc[opt_chain.symbol == symbol, "time_to_expiry"].to_list()[0]


#streaming real time data
feed_token = obj.getfeedToken()
sws = SmartWebSocketV2(data["data"]["jwtToken"], key_secret[0], key_secret[2], feed_token)

correlation_id = "stream_1" #any string value which will help identify the specific streaming in case of concurrent streaming
action = 1 #1 subscribe, 0 unsubscribe
mode = 3 #1 for LTP, 2 for Quote and 3 for SnapQuote

token_list = [{"exchangeType": 2, "tokens": tokens}]


def on_data(wsapp, message):
    option_data[symbol_dict[message['token']]]["price"] = float(message["last_traded_price"])
    option_data[symbol_dict[message['token']]]["oi"] = int(message["open_interest"])
    option_data[symbol_dict[message['token']]]["volume"] = int(message["volume_trade_for_the_day"])
    option_data[symbol_dict[message['token']]]["bid"] = float(message["best_5_buy_data"][0]["price"])
    option_data[symbol_dict[message['token']]]["ask"] = float(message["best_5_sell_data"][0]["price"])
    option_data[symbol_dict[message['token']]]["mid_price"] = (float(message["best_5_buy_data"][0]["price"]) + float(message["best_5_sell_data"][0]["price"]))/2


def on_open(wsapp):
    print("on open")
    sws.subscribe(correlation_id, mode, token_list)


def on_error(wsapp, error):
    print(error)


# Assign the callbacks.
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error

def connection_fun():
    sws.connect()
    
con_thread = threading.Thread(target=connection_fun, daemon=True)
con_thread.start()
time.sleep(3)

# calculate and update option greeks using real time market data
ir = 0.07

for option in option_data:
    up = obj.ltpData("NSE", "BANKNIFTY-EQ", "26009")["data"]["ltp"]
    mbo = mibian.BS([up, option_data[option]["strike"], ir, option_data[option]["time_to_expiry"]], callPrice= option_data[option]["price"])
    option_data[option]["imp_vol"] = mbo.impliedVolatility
    
    mbo = mibian.BS([up, option_data[option]["strike"], ir, option_data[option]["time_to_expiry"]], volatility= option_data[option]["imp_vol"])
    option_data[option]["delta"] = mbo.callDelta if option_data[option]["type"] =="CE" else mbo.putDelta
    option_data[option]["theta"] =mbo.callTheta if option_data[option]["type"]=="CE" else mbo.putTheta
    option_data[option]["vega"] =mbo.vega
    option_data[option]["gamma"] =mbo.gamma





