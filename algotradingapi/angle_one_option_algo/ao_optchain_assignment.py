# -*- coding: utf-8 -*-
"""
Angel One - Assignment1

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

from smartapi import SmartConnect
import os
import urllib
import json
import pandas as pd
import numpy as np
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
def option_contracts(ticker, option_type="CE"):
    option_contracts = []
    for instrument in instrument_list:
        if instrument["name"]==ticker and instrument["instrumenttype"] in ["OPTSTK","OPTIDX"] and instrument["symbol"][-2:]==option_type:
            option_contracts.append(instrument)
    return pd.DataFrame(option_contracts)

#get underlying price
underlying_price = obj.ltpData("NSE", "BANKNIFTY-EQ", "26009")["data"]["ltp"]

#part 1
#function to extract atm option contract with closest expiry       
def option_contract_atm_closest(ticker, underlying_price):
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    df_opt_contracts["strike"] = pd.to_numeric(df_opt_contracts["strike"])/100
    atm_strike = df_opt_contracts.loc[abs(df_opt_contracts["strike"] - underlying_price).argmin(),'strike']    
    return (df_opt_contracts[df_opt_contracts["strike"] == atm_strike]).sort_values(by=["time_to_expiry"]).reset_index(drop=True).iloc[0,:]
    
#function to extract atm option contract with user defined expiry
def option_contract_atm_defined_expiry(ticker, underlying_price,expiry_date):
    #expirt_date format needs to be DDMONYYYY e.g. 08SEP2023
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts = df_opt_contracts[df_opt_contracts["expiry"]==expiry_date].reset_index(drop=True)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    df_opt_contracts["strike"] = pd.to_numeric(df_opt_contracts["strike"])/100
    atm_strike = df_opt_contracts.loc[abs(df_opt_contracts["strike"] - underlying_price).argmin(),'strike']    
    return (df_opt_contracts[df_opt_contracts["strike"] == atm_strike]).sort_values(by=["time_to_expiry"]).reset_index(drop=True).iloc[0,:]


atm_opt_contract_closest = option_contract_atm_closest("BANKNIFTY", underlying_price)
atm_opt_contract_def_expiry = option_contract_atm_defined_expiry("BANKNIFTY", underlying_price, "28SEP2023")

#part 2
#function to extract option chain on both sides of the atm with user defined expiry
def option_chain_stack(ticker, underlying_price, duration = 0, num=5):
    #duration = 0 means the closest expiry, 1 means the next closest and so on
    #num =5 means return 5 option contracts closest to the market
    prefix = int(num/2)
    suffix = num - prefix
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    df_opt_contracts["strike"] = pd.to_numeric(df_opt_contracts["strike"])/100
    min_day_count = np.sort(df_opt_contracts["time_to_expiry"].unique())[duration]    
    temp = (df_opt_contracts[df_opt_contracts["time_to_expiry"] == min_day_count]).reset_index(drop=True)
    temp.sort_values(by=["strike"],inplace=True, ignore_index=True)
    atm_idx = abs(temp["strike"] - underlying_price).argmin()
    return temp.iloc[atm_idx-prefix:atm_idx+suffix].reset_index(drop=True)

opt_chain = option_chain_stack("BANKNIFTY", underlying_price, duration = 0, num=5)
