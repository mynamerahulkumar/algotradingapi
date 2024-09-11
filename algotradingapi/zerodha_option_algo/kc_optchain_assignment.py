# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect - Assignment 1

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
from kiteconnect import KiteConnect
import os
import pandas as pd
import numpy as np
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
def option_contracts(ticker, option_type="CE"):
    option_contracts = []
    for instrument in instrument_list:
        if instrument["name"]==ticker and instrument["instrument_type"]==option_type:
            option_contracts.append(instrument)
    return pd.DataFrame(option_contracts)

underlying_price = kite.quote("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
 
#part 1
#function to extract atm option contract with closest expiry       
def option_contract_atm_closest(ticker, underlying_price):
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    atm_strike = df_opt_contracts.loc[abs(df_opt_contracts["strike"] - underlying_price).argmin(),'strike']    
    return (df_opt_contracts[df_opt_contracts["strike"] == atm_strike]).sort_values(by=["time_to_expiry"]).reset_index(drop=True).iloc[0,:]

#function to extract atm option contract with user defined expiry
def option_contract_atm_defined_expiry(ticker, underlying_price,expiry_date):
    #expirt_date format needs to be YYYY-MM-DD
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts = df_opt_contracts[df_opt_contracts["expiry"]==dt.datetime.strptime(expiry_date,"%Y-%m-%d").date()].reset_index(drop=True)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    atm_strike = df_opt_contracts.loc[abs(df_opt_contracts["strike"] - underlying_price).argmin(),'strike']    
    return (df_opt_contracts[df_opt_contracts["strike"] == atm_strike]).sort_values(by=["time_to_expiry"]).reset_index(drop=True).iloc[0,:]

    
atm_opt_contract_closest = option_contract_atm_closest("BANKNIFTY", underlying_price)
atm_opt_contract_def_expiry = option_contract_atm_defined_expiry("BANKNIFTY", underlying_price, "2023-09-28")

#part 2
#function to extract option chain on both sides of the atm with user defined expiry
def option_chain_stack(ticker, underlying_price, duration = 0, num=5):
    #duration = 0 means the closest expiry, 1 means the next closest and so on
    #num =5 means return 5 option contracts closest to the market
    prefix = int(num/2)
    suffix = num - prefix
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    min_day_count = np.sort(df_opt_contracts["time_to_expiry"].unique())[duration]
    
    temp = (df_opt_contracts[df_opt_contracts["time_to_expiry"] == min_day_count]).reset_index(drop=True)
    temp.sort_values(by=["strike"],inplace=True, ignore_index=True)
    atm_idx = abs(temp["strike"] - underlying_price).argmin()
    return temp.iloc[atm_idx-prefix:atm_idx+suffix].reset_index(drop=True)

opt_chain = option_chain_stack("BANKNIFTY", underlying_price, duration = 0, num=5)