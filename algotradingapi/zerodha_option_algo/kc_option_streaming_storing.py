# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect - Streaming option data and storing all relavant information

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import os
import datetime as dt
import mibian
import pandas as pd
import time

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

def option_contracts_atm(ticker, underlying_price):
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    atm_strike = df_opt_contracts.loc[abs(df_opt_contracts["strike"] - underlying_price).argmin(),'strike']    
    return (df_opt_contracts[df_opt_contracts["strike"] == atm_strike]).reset_index(drop=True).iloc[:4,:]

#underlying price
underlying_price = kite.quote("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
    
opt_chain = option_contracts_atm("BANKNIFTY", underlying_price)
opt_chain = opt_chain.sort_values(by=["time_to_expiry"], ignore_index=True)

tokens = opt_chain["instrument_token"].to_list()
symbol_dict = dict(zip(opt_chain.instrument_token, opt_chain.tradingsymbol))
option_data = {symbol_dict[i]:{} for i in tokens}

for symbol in opt_chain.tradingsymbol:
    option_data[symbol]["strike"] = opt_chain.loc[opt_chain.tradingsymbol == symbol, "strike"].to_list()[0]
    option_data[symbol]["type"] = opt_chain.loc[opt_chain.tradingsymbol == symbol, "instrument_type"].to_list()[0]
    option_data[symbol]["time_to_expiry"] = opt_chain.loc[opt_chain.tradingsymbol == symbol, "time_to_expiry"].to_list()[0]
    
# Initialise
kws = KiteTicker(key_secret[0], kite.access_token)

def on_ticks(ws, ticks):
    # Callback to receive ticks.
    for tick in ticks:
        option_data[symbol_dict[tick['instrument_token']]]["price"] = float(tick["last_price"])
        option_data[symbol_dict[tick['instrument_token']]]["oi"] = int(tick["oi"])
        option_data[symbol_dict[tick['instrument_token']]]["volume"] = int(tick["volume_traded"])
        option_data[symbol_dict[tick['instrument_token']]]["bid"] = float(tick["depth"]["buy"][0]["price"])
        option_data[symbol_dict[tick['instrument_token']]]["ask"] = float(tick["depth"]["sell"][0]["price"])
        option_data[symbol_dict[tick['instrument_token']]]["mid_price"] = (float(tick["depth"]["buy"][0]["price"]) + float(tick["depth"]["sell"][0]["price"]))/2

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
time.sleep(3)

# calculate and update option greeks using real time market data
ir = 0.07

for option in option_data:
    up = kite.quote("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
    mbo = mibian.BS([up, option_data[option]["strike"], ir, option_data[option]["time_to_expiry"]], callPrice= option_data[option]["price"])
    option_data[option]["imp_vol"] = mbo.impliedVolatility
    
    mbo = mibian.BS([up, option_data[option]["strike"], ir, option_data[option]["time_to_expiry"]], volatility= option_data[option]["imp_vol"])
    option_data[option]["delta"] = mbo.callDelta if option_data[option]["type"] =="CE" else mbo.putDelta
    option_data[option]["theta"] =mbo.callTheta if option_data[option]["type"]=="CE" else mbo.putTheta
    option_data[option]["vega"] =mbo.vega
    option_data[option]["gamma"] =mbo.gamma

