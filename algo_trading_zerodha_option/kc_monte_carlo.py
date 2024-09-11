# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect - Monte Carlo simulation for pricing options

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
from kiteconnect import KiteConnect
import os
import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt


cwd = os.chdir("D:\\OneDrive\\Udemy\\Zerodha KiteConnect API\\1_account_authorization")

#generate trading session
access_token = open("access_token.txt",'r').read()
key_secret = open("api_key.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)

#get dump of all NFO instruments
instrument_list = kite.instruments("NFO")

#function to extract all option contracts for a given ticker        
def option_contracts(ticker, option_type="CE", exchange="NFO"):
    option_contracts = []
    for instrument in instrument_list:
        if instrument["name"]==ticker and instrument["instrument_type"]==option_type:
            option_contracts.append(instrument)
    return pd.DataFrame(option_contracts)

#function to extract closest strike options to the underlying price
underlying_price = kite.quote("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
        
def option_contracts_atm(ticker, underlying_price, option_type="CE", exchange="NFO"):
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    atm_strike = df_opt_contracts.loc[abs(df_opt_contracts["strike"] - underlying_price).argmin(),'strike']    
    return (df_opt_contracts[df_opt_contracts["strike"] == atm_strike]).reset_index(drop=True).iloc[:4,:]
    
opt_chain = option_contracts_atm("BANKNIFTY", underlying_price)
opt_chain = opt_chain.sort_values(by=["time_to_expiry"], ignore_index=True)

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
    