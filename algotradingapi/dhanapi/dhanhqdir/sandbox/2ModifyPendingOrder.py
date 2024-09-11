import http.client

conn = http.client.HTTPSConnection("api.dhan.co")
import pandas as pd
client_id=""
access_token=".."

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