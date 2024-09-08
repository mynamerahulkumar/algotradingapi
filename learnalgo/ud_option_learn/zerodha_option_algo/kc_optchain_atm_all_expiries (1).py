# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect - Option chain having atm call option contracts for different expiries

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
from kiteconnect import KiteConnect
import os
import pandas as pd
import datetime as dt


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
        
def option_contracts_atm(ticker, underlying_price):
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    atm_strike = df_opt_contracts.loc[abs(df_opt_contracts["strike"] - underlying_price).argmin(),'strike']    
    return (df_opt_contracts[df_opt_contracts["strike"] == atm_strike]).sort_values(by=["time_to_expiry"]).reset_index(drop=True).iloc[:4,:]
    
opt_chain = option_contracts_atm("BANKNIFTY", underlying_price)
