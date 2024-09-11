# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect - getting order level margin details

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
from kiteconnect import KiteConnect
import os
import datetime as dt
import yfinance as yf
import numpy as np
import pandas as pd

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

#function to extract the closest expiring option contracts
def option_contracts_closest(ticker, duration = 0, option_type="CE", exchange="NFO"):
    #duration = 0 means the closest expiry, 1 means the next closest and so on
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) - dt.datetime.now()).dt.days
    min_day_count = np.sort(df_opt_contracts["time_to_expiry"].unique())[duration]
    
    return (df_opt_contracts[df_opt_contracts["time_to_expiry"] == min_day_count]).reset_index(drop=True)

#function to extract closest strike options to the underlying price
underlying_price = kite.quote("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]

#function to extract n closest options to the underlying price
def option_chain(ticker, underlying_price, duration = 0, num = 5, option_type="CE", exchange="NFO"):
    #duration = 0 means the closest expiry, 1 means the next closest and so on
    #num =5 means return 5 option contracts closest to the market
    df_opt_contracts = option_contracts_closest(ticker,duration)
    df_opt_contracts.sort_values(by=["strike"],inplace=True, ignore_index=True)
    atm_idx = abs(df_opt_contracts["strike"] - underlying_price).argmin()
    up = int(num/2)
    dn = num - up
    return df_opt_contracts.iloc[atm_idx-up:atm_idx+dn]
    
opt_chain = option_chain("BANKNIFTY", underlying_price, 0)


#order level margin details
order_param = [{
                "exchange": "NFO",
                "tradingsymbol": opt_chain.tradingsymbol.to_list()[2],
                "transaction_type": "BUY",
                "variety": "regular",
                "product": "NRML",
                "order_type": "LIMIT",
                "quantity": opt_chain.lot_size.to_list()[2],
                "price": 450
                },
                {
                    "exchange": "NFO",
                    "tradingsymbol": opt_chain.tradingsymbol.to_list()[0],
                    "transaction_type": "SELL",
                    "variety": "regular",
                    "product": "NRML",
                    "order_type": "LIMIT",
                    "quantity": opt_chain.lot_size.to_list()[0],
                    "price": 450
                }]

order_margin = kite.order_margins(order_param)

