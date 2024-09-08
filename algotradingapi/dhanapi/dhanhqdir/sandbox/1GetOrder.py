import http.client
from dhanhq import dhanhq
import pandas as pd
clientid=1103695755
access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzI0MzUxMjk5LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMzY5NTc1NSJ9.0mOPgx7lfTGrAjA0FymdtldZmPEW8wIKe2XLrGxk_Hb6utx3m5sC5qIO4z3eMVXvgEnGo962iFcgFA15aI3hEg"
dhan = dhanhq(clientid,access_token)
conn = http.client.HTTPSConnection("api.dhan.co")

headers = {
    'access-token': access_token,
    'Accept': "application/json"
}

conn.request("GET", "/orders/{order-id}", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))