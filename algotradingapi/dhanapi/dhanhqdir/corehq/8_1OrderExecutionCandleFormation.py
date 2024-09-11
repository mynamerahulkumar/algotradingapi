





from dhanhq import dhanhq
from dhanhq import marketfeed
import pandas as pd
# Add your Dhan Client ID and Access Token
client_id=""
access_token=".."


# Structure for subscribing is ("exchange_segment","security_id")

# Maximum 100 instruments can be subscribed, then use 'subscribe_symbols' function

instruments = [(1, "1333"),(0,"13")]

# Type of data subscription
# subscription_code = marketfeed.Ticker
subscription_code =19

# Ticker - Ticker Data
# Quote - Quote Data
# Depth - Market Depth

def entry_function(message):
    print(message)
async def on_connect(instance):
    print("Connected to websocket")

async def on_message(instance, message):
    print("Received:", message)
    # here we can add entry function
print("Subscription code :", subscription_code)

feed = marketfeed.DhanFeed(client_id,
    access_token,
    instruments,
    subscription_code,
    on_connect=on_connect,
    on_message=on_message)

feed.run_forever()