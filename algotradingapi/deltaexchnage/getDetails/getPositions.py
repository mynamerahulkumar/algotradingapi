# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 15:24:16 2024

@author: LENOVO
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 20:12:09 2024

@author: LENOVO
"""

from delta_rest_client import DeltaRestClient

token_path = "C:/Users/LENOVO/OneDrive/Documents/A_Udeyme/ppts/Algo_trradiing/configs/deltakeyfile.txt"
key_secret = open(token_path,'r').read().split()
api_key=key_secret[0]
api_secret=key_secret[1]
delta_client=DeltaRestClient(
    base_url='https://cdn.india.deltaex.org',
    api_key=api_key,
    api_secret=api_secret
    )

orders = delta_client.get_position(27)

print(orders)