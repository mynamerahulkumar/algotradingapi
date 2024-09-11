# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect - Implied volatility using Black Scholes Price

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
from kiteconnect import KiteConnect
import os
import numpy as np
import pandas as pd
from scipy import stats
import datetime as dt
from scipy import optimize


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
opt_chain['iv'] = opt_chain.apply(lambda x: imp_vol_bsm(underlying_price, x.strike, x.bs_price, x.time_to_expiry/365, ir, x.instrument_type), axis=1)