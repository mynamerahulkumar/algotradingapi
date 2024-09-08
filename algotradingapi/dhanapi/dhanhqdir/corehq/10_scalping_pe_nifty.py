from dhanhq import dhanhq
from dhanhq import marketfeed
import pandas as pd
from datetime import datetime

# Add your Dhan Client ID and Access Token
client_id = 1103695755
client_id_ws="1103695755"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzI0MzUxMjk5LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMzY5NTc1NSJ9.0mOPgx7lfTGrAjA0FymdtldZmPEW8wIKe2XLrGxk_Hb6utx3m5sC5qIO4z3eMVXvgEnGo962iFcgFA15aI3hEg"

instruments = [(2, '74634')]  # instrumentid (second term)# first is enum

subscription_code = 19
dhan = dhanhq(client_id, access_token)


def atm_strike(spot_price):
    atm_strike_price = 0
    if spot_price % 100 < 25:
        atm_strike_price = int(spot_price / 100) * 100
    elif spot_price % 100 >= 25 or spot_price % 100 < 75:
        atm_strike_price = int(spot_price / 100) * 100 + 50
    else:
        atm_strike_price = int(spot_price / 100) * 100 + 100
    return atm_strike_price


nifty_ltp = 24190
atm_strike_price = atm_strike(nifty_ltp)
print(atm_strike_price)

def get_symbol_name(symbol, expiry, strike, strike_type):
    instrument = f'{symbol}-{expiry}-{str(strike)}-{strike_type}'
    return instrument


symbol = 'NIFTY'
expiry = 'Aug2024'
strike = atm_strike_price
strike_type_PE = 'PE'
instrument_pe = get_symbol_name(symbol, expiry, strike, strike_type_PE)
print(instrument_pe)
#
#
# def get_instrument_token():
#     df = pd.read_csv('../config/api-scrip-master.csv')
#     data_dict = {}
#     for index, row, in df.iterrows():
#         trading_symbol = row['SEM_TRADING_SYMBOL']
#         exm_exch_id = row['SEM_EXM_EXCH_ID']
#         if trading_symbol not in data_dict:
#             data_dict[trading_symbol] = {}
#         data_dict[trading_symbol][exm_exch_id] = row.to_dict()
#     return data_dict
#
#
# token_dict = get_instrument_token()
#
#
# pe_id = token_dict[instrument_pe]['NSE']['SEM_SMST_SECURITY_ID']
pe_id=74642
print( pe_id)


def get_exchange(dhan, exchange):
    if exchange == "NSE":
        return dhan.NSE
    elif exchange == "BSE":
        return dhan.BSE


def get_side(dhan, side):
    if side == "BUY":
        return dhan.BUY
    elif side == "SELL":
        return dhan.SELL


def get_order_type(dhan, orderType):
    if orderType == "MARKET":
        return dhan.MARKET
    elif orderType == "LIMIT":
        return dhan.LIMIT


def place_order(dhan, symbol, exchange, side, quantity, order_type, price):
    print("place-order")
    exchange_segment = get_exchange(dhan, exchange)
    print(exchange_segment)
    side = get_side(dhan, side)
    print(side)
    order_type = get_order_type(dhan, order_type)
    print(order_type)
    order_id=dhan.place_order(
        tag='',
        transaction_type=dhan.BUY,
        exchange_segment=dhan.NSE,
        product_type=dhan.INTRA,
        order_type=dhan.MARKET,
        validity='DAY',
        security_id='1333',
        quantity=10,
        disclosed_quantity=0,
        price=0,
        trigger_price=0,
        after_market_order=False,
        amo_time='OPEN',
        bo_profit_value=0,
        bo_stop_loss_Value=0,
        drv_expiry_date=None,
        drv_options_type=None,
        drv_strike_price=None
    )

    # order_id = dhan.place_order(security_id=symbol,  # hdbcbank
    #                             exchange_segment=exchange_segment,
    #                             transaction_type=side,
    #                             quantity=quantity,
    #                             order_type=order_type,
    #                             product_type=dhan.INTRA,
    #                             price=price,
    #                             validity='DAY')
    print(order_id)
    return order_id



start_price_pe = 0


current_price_pe = 0

max_stop_loss = -400

max_profit_take = 300


def get_order_detail(order_id):
    order = dhan.get_order_by_id(order_id)
    print("order-")
    print(order)
    return order
#
#
# def update_start_price_pe():
#     order_pe = get_order_detail(pe_id)
#     print("order_pe--")
#     print(order_pe)
#
#     start_price_pe = get_current_price(order_pe)
#     print("start_price_pe-")
#     print(start_price_pe)
#
#     return start_price_pe
#
#
#
#
#
# def get_current_price(order):
#     print("get_current_price-" )
#     print(order['price'])
#     return order['price']


def entry_condition():
    order_id_pe = place_order(dhan, pe_id, 'NSE', 'BUY', 25, 'MARKET', 0)
    print("order_id_pe")
    print(order_id_pe)
    # update_start_price_pe()
    return


# entry
while True:
    curr_time = datetime.now().strftime("%H:%M:%S")
    entry_flag = 0
    print("entry time")
    print(curr_time)
    if curr_time >= "08:30:00" and entry_flag == 0:
        entry_condition()
        entry_flag = 1
        break
    if entry_flag == 1:
        break
#
#
# def exit_condition():
#     order_id_pe = place_order(dhan, pe_id, 'NSE', 'SELL', 25, 'MARKET', 0)
#     print("exit condition-")
#     print(order_id_pe)
#     return

#
# # exit
# while True:
#     curr_time = datetime.now().strftime("%H:%M:%S")
#     exit_flag = 0
#     print("exit time")
#     print(curr_time)
#     if curr_time >= "09:15:00" and exit_flag == 0:
#         exit_condition()
#         exit_flag = 1
#     if exit_flag == 1:
#         break
#
# #
# # above fun will get stuck till 3.15 we need another function trail loss
# def check_stop_loss():
#     order_pe = get_order_detail(pe_id)
#     total_current_premium = get_current_price(order_pe)
#     total_start_premium = start_price_pe
#     diff_premium = total_current_premium - total_start_premium
#     if (diff_premium < max_stop_loss):
#         exit_condition()
#
#
# def check_take_profit():
#     order_pe = get_order_detail(pe_id)
#     total_current_premium = get_current_price(order_pe)
#     total_start_premium = start_price_pe
#     diff_premium = total_current_premium - total_start_premium
#     if (diff_premium >= max_profit_take):
#         exit_condition()
#
#
# def check_exit():
#     curr_time = datetime.now().strftime("%H:%M:%S")
#     if curr_time >= "15:15:00":
#         exit_condition()
#
#
# async def on_connect(instance):
#     print("Connected to websocket")
#
#
# async def on_message(ws, message):
#     print("Received:", message)
#     check_stop_loss()  # combine premium
#     check_take_profit()  # combine premium
#     check_exit()
#     ws.subscribe_symbols(subscription_code, instruments)
#     # here we can add entry function
#
#
# print("Subscription code :", subscription_code)
#
# ws_client = marketfeed.DhanFeed(client_id_ws,
#                                 access_token,
#                                 instruments,
#                                 subscription_code,
#                                 on_connect=on_connect,
#                                 on_message=on_message)
#
# ws_client.run_forever()