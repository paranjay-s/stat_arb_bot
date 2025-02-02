from config_execution_api import session_private
 
# Check for open positions (trade attivi)
def open_position_confirmation(ticker):
    try:
 
        position = session_private.get_positions(category="linear", symbol=ticker, )
 
 
        if position["retMsg"] == "OK":
            if float(position["result"]["list"][0]["size"]) > 0:
 
                return True
    except:
        return True
    return False
 
 
# Check for active positions (ordini aperti)
def active_position_confirmation(ticker):
    try:
        active_order = session_private.get_open_orders(
            category="linear",
            symbol=ticker,
            openOnly=0,
        )
 
 
        if active_order["retMsg"] == "OK":
            if active_order["result"]["list"] != []:
                return True
    except:
        return True
    return False
 
 
# Get open position price and quantity
def get_open_positions(ticker, direction="Long"):
 
    # Get position
 
    position = session_private.get_positions(category="linear", symbol=ticker, )
    # Construct a response
    if "retMsg" in position.keys():
        if position["retMsg"] == "OK":
            if "symbol" in position["result"]["list"][0]:
                order_price = float(position["result"]["list"][0]["avgPrice"])
                order_quantity = float(position["result"]["list"][0]["size"])
                return order_price, order_quantity
            return (0, 0)
    return (0, 0)
 
 
# Get active position price and quantity
def get_active_positions(ticker):
 
    # Get position
    active_order = session_private.get_open_orders(
            category="linear",
            symbol=ticker,
            openOnly=0,
        )
 
 
    # Construct a response
    if "retMsg" in active_order.keys():
        if active_order["retMsg"] == "OK":
            if active_order["result"]["list"] != []:
                order_price = float(active_order["result"]["list"][0]["price"])
                order_quantity = float(active_order["result"]["list"][0]["qty"])
                return order_price, order_quantity
            return (0, 0)
    return (0, 0)
 
 
# Query existing order
def query_existing_order(ticker, order_id):
 
    # Query order
    order = session_private.get_open_orders(
            category="linear",
            symbol=ticker,
            orderId=order_id,
            openOnly=0,
        )
    # Construct response
    if "retMsg" in order.keys():
        if order["retMsg"] == "OK":
            order_price = float(order["result"]["list"][0]["price"])
            order_quantity = float(order["result"]["list"][0]["qty"])
            order_status = order["result"]["list"][0]['orderStatus']
            return order_price, order_quantity, order_status
    return (0, 0, 0)
