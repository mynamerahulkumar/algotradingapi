# -*- coding: utf-8 -*-
"""
Angel One - Implied volatility using Black Scholes Price

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

from smartapi import SmartConnect
from scipy import stats
from scipy import optimize
import os
import urllib
import json
import numpy as np
import pandas as pd
import datetime as dt
from scipy import optimize
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
opt_chain["market_price"] = np.array([131,292,441,564])

#################Implied Vol Calculation using optimization####################
def imp_vol_bsm(stock_price,strike_price,option_price,time,rate,right="CE"):
    
    def black_scholes(vol):
        d1 = (np.log(stock_price/strike_price) + (rate + 0.5* vol**2)*time)/(vol*np.sqrt(time))
        d2 = (np.log(stock_price/strike_price) + (rate - 0.5* vol**2)*time)/(vol*np.sqrt(time))
        nd1 = stats.norm.cdf(d1)
        nd2 = stats.norm.cdf(d2)
        n_d1 = stats.norm.cdf(-1*d1)
        n_d2 = stats.norm.cdf(-1*d2)
        if right.capitalize()[0] == "C":
            opt_price = round((stock_price*nd1) - (strike_price*np.exp(-1*rate*time)*nd2),3)
        else:
            opt_price = round((strike_price*np.exp(-1*rate*time)*n_d2) - (stock_price*n_d1),3)
        return option_price - opt_price
    
    return optimize.brentq(black_scholes,0.05,0.9,maxiter=1000)


    
ir = 0.07
opt_chain['iv'] = opt_chain.apply(lambda x: imp_vol_bsm(underlying_price, x.strike, x.market_price, x.time_to_expiry/365, ir, x.instrument_type), axis=1)