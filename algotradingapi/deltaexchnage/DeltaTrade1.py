# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 20:12:09 2024

@author: LENOVO
"""

from delta_rest_client import DeltaRestClient
delta_client = DeltaRestClient(
  base_url='https://cdn.india.deltaex.org',
  api_key='M0uEO8OtfypamsDy1HsMaPFDOjiVkU',
  api_secret='LROPSWUKhooQmVsLlfJkLibtI12duLYnDH8FUbDn8GjgJkOWGYv2e8Ce1UoT'
)

orders = delta_client.get_live_orders()

print(orders)