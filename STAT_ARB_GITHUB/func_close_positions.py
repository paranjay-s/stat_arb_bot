from config_execution_api import signal_positive_ticker
from config_execution_api import signal_negative_ticker
from config_execution_api import session_private
 
 
# Get position information
def get_position_info(ticker):
 
    # Declare output variables
    side = ""
    size = 0.0
 
    # Extract position info
    position = session_private.get_positions(category="linear",symbol=ticker,)
    if "retMsg" in position.keys():
        if position["retMsg"] == "OK":
            if len(position["result"]["list"]) == 1:
                if float(position["result"]["list"][0]["size"]) > 0:
                    size = float(position["result"]["list"][0]["size"])
                    if position["result"]["list"][0]["side"] == "Buy":
                        side = "Buy"
                    else:
                        side = "Sell"
 
    # Return output
    return side, size
 
 
#  Place market close order
def place_market_close_order(ticker, side, size):
 
    # Close position
    session_private.place_order(
        category="linear",
        symbol=ticker,
        side=side,
        orderType="Market",
        qty=size,
        timeInForce="GTC",
        reduceOnly=True,
        closeOnTrigger=False)
 
 
 
 
    # Return
    return
 
 
# Close all positions for both tickers
def close_all_positions(kill_switch):
 
    # Cancel all active orders
    session_private.cancel_all_orders(category="linear", symbol=signal_positive_ticker)
    session_private.cancel_all_orders(category="linear", symbol=signal_negative_ticker)
 
    # Get position information
    side_1, size_1 = get_position_info(signal_positive_ticker)
    side_2, size_2 = get_position_info(signal_negative_ticker)
 
 
    if size_1 > 0:
        place_market_close_order(signal_positive_ticker, side_2, size_1) # use side 2
 
    if size_2 > 0:
        place_market_close_order(signal_negative_ticker, side_1, size_2) # use side 1
 
    # Output results
    kill_switch = 0
 
    return kill_switch


