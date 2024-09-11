# -*- coding: utf-8 -*-
"""
Angel One - Bear spread strategy implementation

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import os
import urllib
import json
import pandas as pd
import numpy as np
import datetime as dt
from pyotp import TOTP
import threading
import mibian
import time
import yfinance as yf

key_path = r"C:\Users\Mayank\OneDrive\Udemy\Angel One API"
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

def option_chain_bear_spread(ticker, underlying_price, duration = 0, option_type="CE", exchange="NFO"):
    #duration = 0 means the closest expiry, 1 means the next closest and so on
    #num =5 means return 5 option contracts closest to the market
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    df_opt_contracts["strike"] = pd.to_numeric(df_opt_contracts["strike"])/100
    min_day_count = np.sort(df_opt_contracts["time_to_expiry"].unique())[duration]    
    temp = (df_opt_contracts[df_opt_contracts["time_to_expiry"] == min_day_count]).reset_index(drop=True)
    temp.sort_values(by=["strike"],inplace=True, ignore_index=True)
    atm_idx = abs(temp["strike"] - underlying_price).argmin()
    return temp.iloc[[atm_idx,atm_idx+2]]


opt_chain = option_chain_bear_spread("BANKNIFTY", underlying_price)
opt_chain = opt_chain.sort_values(by=["time_to_expiry"], ignore_index=True)


tokens = opt_chain["token"].to_list()
symbol_dict = dict(zip(opt_chain.token, opt_chain.symbol))
option_data = {symbol_dict[i]:{} for i in tokens}

for symbol in opt_chain.symbol:
    option_data[symbol]["strike"] = opt_chain.loc[opt_chain.symbol == symbol, "strike"].to_list()[0]
    option_data[symbol]["type"] = opt_chain.loc[opt_chain.symbol == symbol, "instrumenttype"].to_list()[0]
    option_data[symbol]["time_to_expiry"] = opt_chain.loc[opt_chain.symbol == symbol, "time_to_expiry"].to_list()[0]


#streaming real time data
feed_token = obj.getfeedToken()
sws = SmartWebSocketV2(data["data"]["jwtToken"], key_secret[0], key_secret[2], feed_token)

correlation_id = "stream_1" #any string value which will help identify the specific streaming in case of concurrent streaming
action = 1 #1 subscribe, 0 unsubscribe
mode = 3 #1 for LTP, 2 for Quote and 3 for SnapQuote

token_list = [{"exchangeType": 2, "tokens": tokens}]


def on_data(wsapp, message):
    option_data[symbol_dict[message['token']]]["price"] = float(message["last_traded_price"])
    option_data[symbol_dict[message['token']]]["oi"] = int(message["open_interest"])
    option_data[symbol_dict[message['token']]]["volume"] = int(message["volume_trade_for_the_day"])
    option_data[symbol_dict[message['token']]]["bid"] = float(message["best_5_buy_data"][0]["price"])
    option_data[symbol_dict[message['token']]]["ask"] = float(message["best_5_sell_data"][0]["price"])
    option_data[symbol_dict[message['token']]]["mid_price"] = (float(message["best_5_buy_data"][0]["price"]) + float(message["best_5_sell_data"][0]["price"]))/2

def on_open(wsapp):
    print("on open")
    sws.subscribe(correlation_id, mode, token_list)

def on_error(wsapp, error):
    print(error)

# Assign the callbacks.
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error

def connection_fun():
    sws.connect()
    
con_thread = threading.Thread(target=connection_fun, daemon=True)
con_thread.start()
time.sleep(3)

# calculate and update option greeks using real time market data
ir = 0.07

for option in option_data:
    up = obj.ltpData("NSE", "BANKNIFTY-EQ", "26009")["data"]["ltp"]
    mbo = mibian.BS([up, option_data[option]["strike"], ir, option_data[option]["time_to_expiry"]], callPrice= option_data[option]["price"])
    option_data[option]["imp_vol"] = mbo.impliedVolatility
    
    mbo = mibian.BS([up, option_data[option]["strike"], ir, option_data[option]["time_to_expiry"]], volatility= option_data[option]["imp_vol"])
    option_data[option]["delta"] = mbo.callDelta if option_data[option]["type"] =="CE" else mbo.putDelta
    option_data[option]["theta"] =mbo.callTheta if option_data[option]["type"]=="CE" else mbo.putTheta
    option_data[option]["vega"] =mbo.vega
    option_data[option]["gamma"] =mbo.gamma

def bollingerBand(df, period=20, multiple=2):
    df["ema"] = df["Adj Close"].ewm(span=period,min_periods=period).mean()
    df["bb_up"] = df["ema"] + multiple*df["Adj Close"].rolling(period).std(ddof=0)
    df["bb_dn"] = df["ema"] - multiple*df["Adj Close"].rolling(period).std(ddof=0)
    

def risk_reward(opt_data):
    strikes = opt_data.strike.to_list()
    price = opt_data.price.to_list()
    risk_to_reward = (float(price[0]) - float(price[1]))/(int(strikes[1]) - int(strikes[0]))
    return round(risk_to_reward,2)


def place_limit_order(order_params):
    response = obj.placeOrder(order_params)
    return response

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

def create_order_params(opt_data):            
    order_params =  [{
                    "variety":"NORMAL",
                    "tradingsymbol": opt_chain.symbol.to_list()[1],
                    "symboltoken": opt_chain.token.to_list()[1],
                    "transactiontype": "BUY",
                    "exchange":"NFO",
                    "ordertype":"LIMIT",
                    "producttype":"CARRYFORWARD",
                    "duration":"DAY",
                    "price":opt_data.price.to_list()[1],
                    "quantity": opt_chain.lotsize.to_list()[1]
                    },
                    {
                    "variety":"NORMAL",
                    "tradingsymbol": opt_chain.symbol.to_list()[0],
                    "symboltoken": opt_chain.token.to_list()[0],
                    "transactiontype": "SELL",
                    "exchange":"NFO",
                    "ordertype":"LIMIT",
                    "producttype":"CARRYFORWARD",
                    "duration":"DAY",
                    "price":opt_data.price.to_list()[0],
                    "quantity": opt_chain.lotsize.to_list()[0]
                    }]
    
    return order_params

def strategy(opt_data):
    pos_df = pd.DataFrame(obj.position()["data"])
    holding_df = pd.DataFrame(obj.holding()["data"])
    ord_df = pd.DataFrame(obj.orderBook()["data"])
    
    option_data_df = pd.DataFrame(opt_data).T
    
    if len(holding_df)>0:
        if len([i for i in holding_df.tradingsymbol if i in option_data_df.index]) > 0:
            return
    
    if len(pos_df)>0:
        if len([i for i in pos_df.tradingsymbol if i in option_data_df.index]) > 0:
            return
    
    if len(ord_df)>0:
        if len([i for i in ord_df.tradingsymbol if i in option_data_df.index]) > 0:
            return
    
    ohlc = yf.download("^NSEBANK", period='55d', interval='5m')
    #ohlc = fetchOHLC(ticker,"5minute",4)
    bollingerBand(ohlc)
    
    if (ohlc["Adj Close"].iloc[-2] > ohlc["bb_up"].iloc[-2]) and \
        (ohlc["Adj Close"].iloc[-1] < ohlc["bb_up"].iloc[-1]):
            if risk_reward(option_data_df) > 0.4:
                order_params = create_order_params(option_data_df)
                print("order placed")
                #placeBasketOrder(order_params)
                
            
starttime = time.time()
timeout = starttime + 60*60*5
while time.time() <= timeout:
    try:
        strategy(option_data)
        time.sleep(300 - ((time.time() - starttime)%300))
    except Exception as e:
        print(e)

