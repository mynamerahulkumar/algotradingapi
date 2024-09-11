# -*- coding: utf-8 -*-
"""
Angel One - Monte Carlo simulation for pricing options

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
from smartapi import SmartConnect
import yfinance as yf
import matplotlib.pyplot as plt
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


#function to extract closest strike options to the underlying price
underlying_price = obj.ltpData("NSE", "BANKNIFTY-EQ", "26009")["data"]["ltp"]

def option_contracts_atm(ticker, underlying_price):
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    df_opt_contracts["strike"] = pd.to_numeric(df_opt_contracts["strike"])/100
    atm_strike = df_opt_contracts.loc[abs(df_opt_contracts["strike"] - underlying_price).argmin(),'strike']    
    return (df_opt_contracts[df_opt_contracts["strike"] == atm_strike]).sort_values(by=["time_to_expiry"]).reset_index(drop=True).iloc[:4,:]
   
opt_chain = option_contracts_atm("BANKNIFTY", underlying_price)
opt_chain["instrument_type"] = opt_chain["symbol"].str[-2:]

#calculate historical volatility
hist_data = yf.download("^NSEBANK", period='1y')
hist_data["return"] = hist_data["Adj Close"].pct_change()
hist_vol = hist_data["return"].std()*np.sqrt(252)

#################Monte Carlo Option pricing Model############################
num_ts = 50
num_path = 1000
def monte_carlo(underlying_price,strike_price,vol,time,rate,right="Call",plot=False):
    paths = []
    for i in range(num_path):
        path = [underlying_price]
        for j in range(num_ts):
            price_new = path[j] * np.exp((rate - 0.5* vol**2)*(time/num_ts) + vol*np.sqrt(time/num_ts)*np.random.normal())
            path.append(price_new)
        paths.append(path)
        
    if plot:
        #plotting paths
        plt.xlabel("time step")
        plt.ylabel("underlying price evolution")
        plt.title("monte carlo simulation")
        for i in range(len(paths)):
            plt.plot([x for x in range(len(paths[0]))],paths[i])
        plt.show()
    
    payoff = 0
    for path in paths:
        if right.capitalize()[0] == "C":
            payoff+=max(path[-1] - strike_price,0)
        else:
            payoff+=max(strike_price - path[-1],0)
    
    return (payoff/num_path)*np.exp(-1*rate*time)

ir = 0.07 
opt_chain['ms_price'] = opt_chain.apply(lambda x: monte_carlo(underlying_price, x.strike, hist_vol, x.time_to_expiry/365, ir, x.instrument_type), axis=1)
    