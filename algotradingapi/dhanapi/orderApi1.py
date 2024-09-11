# -*- coding: utf-8 -*-
client_id=""
access_token=".."




"""
Created on Tue Aug 13 09:27:02 2024

@author: LENOVO
"""


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
        return positions
    return "No Orders"
positions=get_positions(dhan)
holdings=get_holding(dhan)
orders=get_orders(dhan)
print(orders)
