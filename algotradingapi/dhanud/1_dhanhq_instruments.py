# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 20:30:59 2024

@author: LENOVO
"""
import  pandas as pd

def get_instrument_token():
    df=pd.read_csv('C:/Users/LENOVO/Documents/GitHub/algotradingapi/algotradingapi/dhanud/config/api-scrip-master.csv')
    data_dict={}
    for index,row,in df.iterrows():
        trading_symbol=row['SEM_TRADING_SYMBOL'] # trading symbol
        exm_exch_id= row['SEM_EXM_EXCH_ID'] #exchange id under which this trading symbol is trade ,nSE,BSE
        if trading_symbol not in data_dict:
            data_dict[trading_symbol]={}
        data_dict[trading_symbol][exm_exch_id]=row.to_dict()
    return  data_dict

instrument=get_instrument_token()
print(instrument['RELIANCE'])
print(instrument['RELIANCE']['NSE'])
print(instrument['RELIANCE']['NSE']['SEM_SMST_SECURITY_ID'])
instrument_bank=instrument['BANKNIFTY']
print(instrument_bank)
# =============================================================================
# print(token_dict)
# =============================================================================
# =============================================================================
# print(token_dict['RELIANCE'])
# print(token_dict['RELIANCE']['NSE'])
# print(token_dict['RELIANCE']['NSE']['SEM_SMST_SECURITY_ID'])
