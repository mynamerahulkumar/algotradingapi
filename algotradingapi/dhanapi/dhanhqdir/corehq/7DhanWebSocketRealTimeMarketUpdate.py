clientid=1103695755
from dhanhq import dhanhq
import pandas as pd
access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzI3MTA0MjkyLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMzY5NTc1NSJ9.dW3W7NduPmHm6WdDVIjqbU7lYy9P6yX5wJ0LrPnjZ1l2N7kUatY2YgKMyUZ3OivKQlV-HzeqRSdQxWkTUTjtVw"
dhan = dhanhq(clientid,access_token)

def historical_data(dhan,symbol,exchange_segment,instrument_type,from_date,to_date):
    equity_historical_data=dhan.historical_minute_charts(
        symbol=symbol,
        exchange_segment=exchange_segment,
        instrument_type=instrument_type,
        expiry_code=0,
        from_date=from_date,
        to_date=to_date
    )
    print(equity_historical_data)
# =============================================================================
#     df=pd.DataFrame(equity_historical_data['data'])
# =============================================================================
    # df['start_time']=df['start_time']+315569260 #1970+10 (1.3..) epoch number -general use case for python julian year #1980(1.6..)
    # df['symbol']=symbol
# =============================================================================
#     print(df) # use python fun to convert normal date
# =============================================================================
symbol1='TCS'
symbol_list=['TCS','INFY','WIPRO','VBL']
for symbol in symbol_list:
    exchange_segment='NSE_EQ'
    instrument_type='EQUITY'
    from_date='2024-04-07'
    to_date='2024-05-07'
    symbol=symbol
    historical_data(dhan,symbol, exchange_segment, instrument_type, from_date, to_date)
