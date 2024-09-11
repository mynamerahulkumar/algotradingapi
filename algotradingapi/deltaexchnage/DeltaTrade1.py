# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 20:12:09 2024

@author: LENOVO
"""

from delta_rest_client import DeltaRestClient
# =============================================================================
# delta_client = DeltaRestClient(
#   base_url='https://cdn.india.deltaex.org',
#   api_key='',
#   api_secret=''
# )
# =============================================================================

orders = delta_client.get_live_orders()

print(orders)