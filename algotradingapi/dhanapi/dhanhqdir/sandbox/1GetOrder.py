import http.client
from dhanhq import dhanhq
import pandas as pd
client_id=""
access_token=".."
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