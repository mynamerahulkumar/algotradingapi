from dhanhq import dhanhq
import pandas as pd
clientid=1103695755
access_token=".."
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
    # if holdings is not None:
    #      df_holdings=pd.DataFrame(holdings['data'])
    #      return df_holdings
    # return "NO Holdings"

def get_exchange(dhan,exchange):
    if exchange == "NSE":
        return dhan.NSE
    elif exchange == "BSE":
        return dhan.BSE
def get_side(dhan,side):
    if side == "BUY":
        return dhan.BUY
    elif side == "SELL":
        return dhan.SELL

def get_order_type(dhan,orderType):
    if orderType == "MARKET":
        return  dhan.MARKET
    elif orderType == "LIMIT":
        return  dhan.LIMIT
def place_order(dhan,symbol,exchange,side,quantity,order_type,price):
    exchange_segment=get_exchange(dhan,exchange)
    side=get_side(dhan,side)
    order_type=get_order_type(dhan,order_type)
    order_id=dhan.place_order(security_id=symbol,#hdbcbank
                              exchange_segment=exchange_segment,
                              transaction_type=side,
                              quantity=quantity,
                              order_type=order_type,
                              product_type=dhan.INTRA,
                              price=price)
    return order_id

def get_orders(dhan):
    data = dhan.get_order_list()
    if data is not None:
        positions =  pd.DataFrame(data['data'])
        print(positions)
    return "No Orders"
positions=get_positions(dhan)
holdings=get_holding(dhan)
print(positions)
print(holdings)


# symbol='235431'
# exchange = 'NSE'
# side = 'BUY'
# quantity=1
# order_type = 'MARKET'
#
# price =70
#
# place_order(dhan,symbol,exchange,side, quantity,order_type,price)

