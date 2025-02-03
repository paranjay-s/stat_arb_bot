from config_execution_api import session_private
from config_execution_api import limit_order_basis
from config_execution_api import session_public
import time
import hashlib
import hmac
import requests
from config_execution_api import stop_loss_fail_safe
from config_execution_api import ticker_1, ticker_2
from config_execution_api import rounding_ticker_1, rounding_ticker_2
from config_execution_api import quantity_rounding_ticker_1, quantity_rounding_ticker_2
from func_calculations import get_trade_details

# Your API details
api_key = "JwbCSQ82MV7qPlXHYq"
api_secret = "817fNQzINkn1E5KsKN5AxWIqNAKex4UaVWjy"  # Replace with your actual API secret
api_url = "https://api-testnet.bybit.com/v5/order/create"

# Generate the signature
def generate_signature(api_key, api_secret, timestamp, order_data):
    query_string = f"api_key={api_key}&" \
                   f"category={order_data['category']}&" \
                   f"symbol={order_data['symbol']}&" \
                   f"side={order_data['side']}&" \
                   f"orderType={order_data['orderType']}&" \
                   f"qty={order_data['qty']}&" \
                   f"price={order_data['price']}&" \
                   f"timeInForce={order_data['timeInForce']}&" \
                   f"orderLinkId={order_data['orderLinkId']}&" \
                   f"reduceOnly={order_data['reduceOnly']}&" \
                   f"closeOnTrigger={order_data['closeOnTrigger']}&" \
                   f"timestamp={timestamp}"

    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature

# Set leverage function (no change needed here)
def set_leverage(ticker):
    try:
        # Set isolated margin mode
        session_private.set_margin_mode(
            setMarginMode="ISOLATED_MARGIN",
            symbol=ticker
        )
        # Set leverage
        session_private.set_leverage(
            category="linear",
            symbol=ticker,
            buyLeverage="1",
            sellLeverage="1"
        )
    except Exception as e:
        print(f"Error setting leverage: {e}")


def place_order(ticker, price, quantity, direction, stop_loss):
    if direction == "Long":
        side = "Buy"
    else:
        side = "Sell"

    # Remove stop loss from initial market order
    if limit_order_basis:
        order = session_private.place_order(
            category="linear",
            symbol=ticker,
            side=side,
            orderType="Limit",
            qty=quantity,
            price=price,
            timeInForce="PostOnly",
            reduceOnly=False,
            closeOnTrigger=False,
            stopLoss=stop_loss
        )
    else:
        order = session_private.place_order(
            category="linear",
            symbol=ticker,
            side=side,
            orderType="Market",
            qty=quantity,
            timeInForce="GTC",
            reduceOnly=False,
            closeOnTrigger=False,
            # Removed stopLoss parameter
        )
    return order


def initialise_order_execution(ticker, direction, capital):
    orderbook = session_public.get_orderbook(category="linear", symbol=ticker)
    if orderbook:
        mid_price, stop_loss, quantity = get_trade_details(orderbook, direction, capital)
        if quantity > 0:
            order = place_order(ticker, mid_price, quantity, direction, stop_loss)
            if "result" in order.keys() and "orderId" in order["result"]:
                return order["result"]["orderId"], stop_loss  # Return both order ID and stop loss
    return 0, 0  # Return default values if failed
    

def set_stop_loss(ticker, side, stop_loss):
    try:
        session_private.set_trading_stop(
            category="linear",
            symbol=ticker,
            side=side,
            stopLoss=stop_loss
        )
    except Exception as e:
        print(f"Error setting stop loss: {e}")
