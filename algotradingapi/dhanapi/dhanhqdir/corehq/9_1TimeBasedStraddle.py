# from dhanhq import dhanhq
# from dhanhq import marketfeed
# import pandas as pd
# from datetime import  datetime
# # Add your Dhan Client ID and Access Token
#
# instruments=[(0,'13'),(1,'1333'),(7,'1001737'),(8,'869117')] #instrumentid (second term)# first is enum
#
# subscription_code=19
# dhan = dhanhq(clientid,access_token)
# def atm_strike(spot_price):
#     atm_strike_price=0
#     if spot_price%100<25:
#         atm_strike_price=int(spot_price/100)*100
#     elif spot_price %100 >=25 or spot_price%100<75:
#         atm_strike_price=int(spot_price/100)*100+50
#     else:
#         atm_strike_price=int(spot_price/100)*100+100
#     return  atm_strike_price
#
# nifty_ltp=24055
# atm_strike_price=atm_strike(nifty_ltp)
# def get_symbol_name(symbol,expiry,strike,strike_type):
#     instrument= f'{symbol}-{expiry}-{str(strike)}-{strike_type}'
#     return  instrument
#
# symbol='NIFTY'
# expiry='Sep2024'
# strike=atm_strike_price
# strike_type_CE='CE'
# strike_type_PE='PE'
# instrument_ce=get_symbol_name(symbol, expiry, strike, strike_type_CE)
# instrument_pe=get_symbol_name(symbol, expiry, strike, strike_type_PE)
# print(instrument_ce,instrument_pe)
#
# def get_instrument_token():
#     df=pd.read_csv('../config/api-scrip-master.csv')
#     data_dict={}
#     for index,row,in df.iterrows():
#         trading_symbol=row['SEM_TRADING_SYMBOL']
#         exm_exch_id= row['SEM_EXM_EXCH_ID']
#         if trading_symbol not in data_dict:
#             data_dict[trading_symbol]={}
#         data_dict[trading_symbol][exm_exch_id]=row.to_dict()
#     return  data_dict
#
# token_dict=get_instrument_token()
#
# ce_id=token_dict[instrument_ce]['NSE']['SEM_SMST_SECURITY_ID']
#
# pe_id=token_dict[instrument_pe]['NSE']['SEM_SMST_SECURITY_ID']
#
# print(ce_id,pe_id)
# def get_exchange(dhan,exchange):
#     if exchange == "NSE":
#         return dhan.NSE
#     elif exchange == "BSE":
#         return dhan.BSE
# def get_side(dhan,side):
#     if side == "BUY":
#         return dhan.BUY
#     elif side == "SELL":
#         return dhan.SELL
#
# def get_order_type(dhan,orderType):
#     if orderType == "MARKET":
#         return  dhan.MARKET
#     elif orderType == "LIMIT":
#         return  dhan.LIMIT
# def place_order(dhan,symbol,exchange,side,quantity,order_type,price):
#     exchange_segment=get_exchange(dhan,exchange)
#     side=get_side(dhan,side)
#     order_type=get_order_type(dhan,order_type)
#     order_id=dhan.place_order(security_id=symbol,#hdbcbank
#                               exchange_segment=exchange_segment,
#                               transaction_type=side,
#                               quantity=quantity,
#                               order_type=order_type,
#                               product_type=dhan.INTRA,
#                               price=price)
#     return order_id
#
# def entry_condition():
#     order_id_ce = place_order(dhan,ce_id,'NSE','SELL',50,'MARKET',0)
#     order_id_pe = place_order(dhan,pe_id,'NSE','SELL',50,'MARKET',0)
#     return
#
# # entry
# while True:
#     curr_time=datetime.now().strftime("%H:%M:%S")
#     entry_flag=0
#     if curr_time >= "09:30:00" and entry_flag==0:
#         entry_condition()
#         entry_flag = 1
#     if entry_flag == 1:
#         break
# def exit_condition():
#     order_id_ce = place_order(dhan,ce_id,'NSE','BUY',50,'MARKET',0)
#     order_id_pe = place_order(dhan,pe_id,'NSE','BUY',50,'MARKET',0)
#     return
#
#
# # exit
# while True:
#     curr_time=datetime.now().strftime("%H:%M:%S")
#     exit_flag=0
#     if curr_time >= "15:15:00" and exit_flag==0:
#         exit_condition()
#         exit_flag = 1
#     if exit_flag == 1:
#         break
#
# # above fun will get stuck till 3.15 we need another function trail loss