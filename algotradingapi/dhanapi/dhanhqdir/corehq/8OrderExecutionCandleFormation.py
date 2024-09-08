# from dhanhq import dhanhq
# import pandas as pd
# clientid=1103695755
# access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzI0MzUxMjk5LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMzY5NTc1NSJ9.0mOPgx7lfTGrAjA0FymdtldZmPEW8wIKe2XLrGxk_Hb6utx3m5sC5qIO4z3eMVXvgEnGo962iFcgFA15aI3hEg"
# dhan = dhanhq(clientid,access_token)
# #https://dhanhq.co/docs/v1/annexure/
# instruments=[(0,'13'),(1,'1333'),(7,'1001737'),(8,'869117')] #instrumentid (second term)# first is enum
# subsciption_code=19 #Feed request code #market depth
# # usage example
#
# #continously running
# async  def on_connect(instance):
#     print("Connected in callback")
#
#
# async  def on_message(ws,message):
#     print('Received in callback',message)
#     ws.subscribe_symbols(subsciption_code,instruments)
#
# print("Subscription code",subsciption_code)
#
# ws_client=
#
#
