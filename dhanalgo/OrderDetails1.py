clientid=11036957

access_token=""
from dhanhq import dhanhq
import pandas as pd

dhan = dhanhq(clientid,access_token)
def get_positions(dhan):
    positions=dhan.get_positions()
    if positions is not None:
       df_position=pd.DataFrame(positions['data'])
       return df_position
    return  "NO Positions"
def get_holding(dhan):
    holdings=dhan.get_holdings()
    print(holdings)



def get_orders(dhan):
    data = dhan.get_order_list()
    if data is not None:
        positions =  pd.DataFrame(data['data'])
        print(positions)
    return "No Orders"
positions=get_positions(dhan)
holdings=get_holding(dhan)
print(positions)
print(holdings)