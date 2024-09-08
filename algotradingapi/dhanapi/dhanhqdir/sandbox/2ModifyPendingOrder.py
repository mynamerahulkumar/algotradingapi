import http.client

conn = http.client.HTTPSConnection("api.dhan.co")
import pandas as pd
clientid=1103695755
access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzI0MzUxMjk5LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMzY5NTc1NSJ9.0mOPgx7lfTGrAjA0FymdtldZmPEW8wIKe2XLrGxk_Hb6utx3m5sC5qIO4z3eMVXvgEnGo962iFcgFA15aI3hEg"
dhan = dhanhq(clientid,access_token)
conn = http.client.HTTPSConnection("api.dhan.co")
payload = "{\n  \"dhanClientId\": \"string\",\n  \"orderId\": \"string\",\n  \"orderType\": \"LIMIT\",\n  \"legName\": \"ENTRY_LEG\",\n  \"quantity\": -2147483648,\n  \"price\": -3.402823669209385e+38,\n  \"disclosedQuantity\": -2147483648,\n  \"triggerPrice\": -3.402823669209385e+38,\n  \"validity\": \"DAY\"\n}"

headers = {
    'access-token': access_token,
    'Content-Type': "application/json",
    'Accept': "application/json"
}

conn.request("PUT", "/orders/{order-id}", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))