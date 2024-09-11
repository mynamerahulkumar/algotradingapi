# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect - Bear spread strategy implementation

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import os
import datetime as dt
import mibian
import pandas as pd
import time
import numpy as np
import yfinance as yf

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

def option_chain_bear_spread(ticker, underlying_price, duration = 0, option_type="CE", exchange="NFO"):
    #duration = 0 means the closest expiry, 1 means the next closest and so on
    #num =5 means return 5 option contracts closest to the market
    df_opt_contracts = option_contracts(ticker)
    df_opt_contracts["time_to_expiry"] = (pd.to_datetime(df_opt_contracts["expiry"]) + dt.timedelta(0,16*3600) - dt.datetime.now()).dt.total_seconds() / dt.timedelta(days=1).total_seconds() # add 1 to get around the issue of time to expiry becoming 0 for options maturing on trading day   
    min_day_count = np.sort(df_opt_contracts["time_to_expiry"].unique())[duration]
    
    temp = (df_opt_contracts[df_opt_contracts["time_to_expiry"] == min_day_count]).reset_index(drop=True)
    temp.sort_values(by=["strike"],inplace=True, ignore_index=True)
    atm_idx = abs(temp["strike"] - underlying_price).argmin()
    return temp.iloc[[atm_idx,atm_idx+2]]

#underlying price
underlying_price = kite.quote("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
    
opt_chain = option_chain_bear_spread("BANKNIFTY", underlying_price)
opt_chain = opt_chain.sort_values(by=["time_to_expiry"], ignore_index=True)

tokens = opt_chain["instrument_token"].to_list()
symbol_dict = dict(zip(opt_chain.instrument_token, opt_chain.tradingsymbol))
option_data = {symbol_dict[i]:{} for i in tokens}

for symbol in opt_chain.tradingsymbol:
    option_data[symbol]["strike"] = opt_chain.loc[opt_chain.tradingsymbol == symbol, "strike"].to_list()[0]
    option_data[symbol]["type"] = opt_chain.loc[opt_chain.tradingsymbol == symbol, "instrument_type"].to_list()[0]
    option_data[symbol]["time_to_expiry"] = opt_chain.loc[opt_chain.tradingsymbol == symbol, "time_to_expiry"].to_list()[0]
    option_data[symbol]["lot_size"] = opt_chain.loc[opt_chain.tradingsymbol == symbol, "lot_size"].to_list()[0]
    
# Initialise
kws = KiteTicker(key_secret[0], kite.access_token)

def on_ticks(ws, ticks):
    # Callback to receive ticks.
    for tick in ticks:
        option_data[symbol_dict[tick['instrument_token']]]["price"] = float(tick["last_price"])
        option_data[symbol_dict[tick['instrument_token']]]["oi"] = int(tick["oi"])
        option_data[symbol_dict[tick['instrument_token']]]["volume"] = int(tick["volume_traded"])
        option_data[symbol_dict[tick['instrument_token']]]["bid"] = float(tick["depth"]["buy"][0]["price"])
        option_data[symbol_dict[tick['instrument_token']]]["ask"] = float(tick["depth"]["sell"][0]["price"])
        option_data[symbol_dict[tick['instrument_token']]]["mid_price"] = (float(tick["depth"]["buy"][0]["price"]) + float(tick["depth"]["sell"][0]["price"]))/2

def on_connect(ws, response):
    # Callback on successful connect.
    ws.subscribe(tokens)
    ws.set_mode(ws.MODE_FULL, tokens)

def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.connect(threaded=True) #multithreaded application
time.sleep(3)

# calculate and update option greeks using real time market data
ir = 0.07

for option in option_data:
    up = kite.quote("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
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

def check_margin(order_param,threshold=0.5):
    margin = kite.margins()   
    cash_avl = margin["equity"]["net"]
    bskt_order_margin = kite.basket_order_margins(order_param)
    req_margin = bskt_order_margin["final"]["total"]
    if float(req_margin) < threshold*cash_avl:
        return True
    else:
        return

def placeLimitOrder(order_params):    
    # Place an intraday limit order on NFO
    order_id = kite.place_order(tradingsymbol=order_params['tradingsymbol'],
                                exchange=order_params['exchange'],
                                transaction_type=order_params['transaction_type'],
                                quantity=order_params['quantity'],
                                price=order_params['price'],
                                order_type=order_params['order_type'],
                                product=order_params['product'],
                                variety=order_params['variety'])
    return order_id

def order_status_check(ord_id):
    pending_complete = True
    while pending_complete:
        orders = kite.orders()
        orders_df = pd.DataFrame(orders)
        status = orders_df.loc[orders_df.order_id == ord_id, "status"].to_list()[0]
        if status == "COMPLETE":
            break
        time.sleep(10)
        

def placeBasketOrder(order_param_list, assure_execution=[0]):
    #the first order param in the list should be the buy/hedge order
    for count, order in enumerate(order_param_list):
        order_id = placeLimitOrder(order)
        if count in assure_execution:
            order_status_check(order_id)
            
def create_order_params(opt_data):
    order_param = [{
                "exchange": "NFO",
                "tradingsymbol": opt_data.index.to_list()[1],
                "transaction_type": "BUY",
                "variety": "regular",
                "product": "NRML",
                "order_type": "LIMIT",
                "quantity": opt_chain.lot_size.to_list()[1],
                "price": opt_data.price.to_list()[1]
                },
                {
                "exchange": "NFO",
                "tradingsymbol": opt_data.index.to_list()[0],
                "transaction_type": "SELL",
                "variety": "regular",
                "product": "NRML",
                "order_type": "LIMIT",
                "quantity": opt_chain.lot_size.to_list()[0],
                "price": opt_data.price.to_list()[0]
                }]
    return order_param

def strategy(opt_data):
    pos_df = pd.DataFrame(kite.positions()["day"])
    holding_df = pd.DataFrame(kite.holdings())
    ord_df = pd.DataFrame(kite.orders())
    
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
                if check_margin(order_params):
                    print("order placed")
                    #placeBasketOrder(order_params)
                else:
                    print("insufficient margin to place order")
                

            
starttime = time.time()
timeout = starttime + 60*60*5
while time.time() <= timeout:
    try:
        strategy(option_data)
        time.sleep(300 - ((time.time() - starttime)%300))
    except Exception as e:
        print(e)
        
