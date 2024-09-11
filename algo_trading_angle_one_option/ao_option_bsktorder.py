# -*- coding: utf-8 -*-
"""
Angel One - placing basket order

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

from smartapi import SmartConnect
import os
import urllib
import json
import pandas as pd
import datetime as dt
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

def option_contracts_atm(ticker, underlying_price):
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    df_opt_contracts.sort_values(by=["time_to_expiry"],inplace=True, ignore_index=True)
    atm_strike = df_opt_contracts.loc[abs(pd.to_numeric(df_opt_contracts["strike"])/100 - underlying_price).argmin(),'strike']    
    return (df_opt_contracts[df_opt_contracts["strike"] == atm_strike]).reset_index(drop=True).iloc[:4,:]

underlying_price = obj.ltpData("NSE", "BANKNIFTY-EQ", "26009")["data"]["ltp"]

opt_chain = option_contracts_atm("BANKNIFTY", underlying_price)
opt_chain = opt_chain.sort_values(by=["time_to_expiry"], ignore_index=True)
opt_chain["strike"] = pd.to_numeric(opt_chain["strike"])/100
opt_chain["instrument_type"] = opt_chain["symbol"].str[-2:]


rms = obj.rmsLimit() #intial margin
cash_balance = float(rms["data"]["availablecash"])

def place_limit_order(order_params):
    response = obj.placeOrder(order_params)
    return response


order_params =  [{
                "variety":"NORMAL",
                "tradingsymbol": opt_chain.symbol.to_list()[2],
                "symboltoken": opt_chain.token.to_list()[2],
                "transactiontype": "BUY",
                "exchange":"NFO",
                "ordertype":"LIMIT",
                "producttype":"CARRYFORWARD",
                "duration":"DAY",
                "price":120,
                "quantity": opt_chain.lotsize.to_list()[2]
                },
                {
                "variety":"NORMAL",
                "tradingsymbol": opt_chain.symbol.to_list()[1],
                "symboltoken": opt_chain.token.to_list()[1],
                "transactiontype": "SELL",
                "exchange":"NFO",
                "ordertype":"LIMIT",
                "producttype":"CARRYFORWARD",
                "duration":"DAY",
                "price":450,
                "quantity": opt_chain.lotsize.to_list()[1]
                }]

def order_status_check(ord_id):
    #this function stops the code execution unless the order_id's status turns to COMPLETE
    pending_complete = True
    while pending_complete:
        orders = obj.orderBook()
        orders_df = pd.DataFrame(orders["data"])
        orderstatus = orders_df.loc[orders_df.orderid==ord_id, "orderstatus"].to_list()[0]
        if orderstatus=="complete":
            break
        time.sleep(10)
        
def placeBasketOrder(order_param_list, assure_execution=[0]):
    for count, order in enumerate(order_param_list):
        order_id = place_limit_order(order)
        if count in assure_execution:
            order_status_check(order_id)    
                
    
