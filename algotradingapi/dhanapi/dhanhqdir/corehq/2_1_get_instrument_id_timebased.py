import  pandas as pd

def get_instrument_token():
    df=pd.read_csv('../config/api-scrip-master.csv')
    data_dict={}
    for index,row,in df.iterrows():
        trading_symbol=row['SEM_TRADING_SYMBOL']
        exm_exch_id= row['SEM_EXM_EXCH_ID']
        if trading_symbol not in data_dict:
            data_dict[trading_symbol]={}
        data_dict[trading_symbol][exm_exch_id]=row.to_dict()
    return  data_dict

token_dict=get_instrument_token()
# =============================================================================
# print(token_dict)
# =============================================================================
# =============================================================================
# print(token_dict['RELIANCE'])
# print(token_dict['RELIANCE']['NSE'])
# print(token_dict['RELIANCE']['NSE']['SEM_SMST_SECURITY_ID'])
# =============================================================================

def get_symbol_name(symbol,expiry,strike,strike_type):
    instrument= f'{symbol}-{expiry}-{str(strike)}-{strike_type}'
    return  instrument

symbol='BANKNIFTY'
expiry='Sep2024'
strike=50400
strike_type='PE'
instrument=get_symbol_name(symbol, expiry, strike, strike_type)
print(instrument)
#
# =============================================================================
# print(token_dict[instrument])
# 
print(token_dict[instrument]['NSE'])
# 
# =============================================================================
print(token_dict[instrument]['NSE']['SEM_LOT_UNITS'])

print(token_dict[instrument]['NSE']['SEM_SMST_SECURITY_ID'])
print(token_dict[instrument]['NSE']['SEM_CUSTOM_SYMBOL'])

