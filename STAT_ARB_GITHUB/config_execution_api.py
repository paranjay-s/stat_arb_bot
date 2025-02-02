
"""
API Documentation
https://bybit-exchange.github.io/docs/v5/intro
"""

# API Imports
from pybit.unified_trading import HTTP

# CONFIG VARIABLES

testnet = True        #CHANGE IT TO FALSE FOR SHIFTING TO MAIN NET
ticker_1 = "BCHUSDT"   #This is an example, you can change the ticker according to your list of cointegrated pairs, maybe you can take help from the excel files provided by me in the repository
ticker_2 = "XNOUSDT"   #This is an example, you can change the ticker according to your list of cointegrated pairs, maybe you can take help from the excel files provided by me in the repository
signal_positive_ticker = ticker_2
signal_negative_ticker = ticker_1
rounding_ticker_1 = 2     #modify the rounding as per ByBit, For example- BTCUSDT CP is 101499.15, so the rounding value is 2 
rounding_ticker_2 = 2     #modify the rounding as per ByBit, For example- BTCUSDT CP is 101499.15, so the rounding value is 2 
quantity_rounding_ticker_1 = 3     #modify the quantity rounding as per the ticker, For example in ByBit the quantity rounding for BTCUSDT is 3 like 0.001
quantity_rounding_ticker_2 = 2     #modify the quantity rounding as per the ticker, For example in ByBit the quantity rounding for BTCUSDT is 3 like 0.001

# LIVE API
api_key_mainnet = "enter your mainnet API key"    
api_secret_mainnet = "insert your key here"

# TEST API
api_key_testnet = "enter your testnet API key"
api_secret_testnet = "insert your key here"

# SELECTED API
api_key = api_key_testnet if testnet else api_key_mainnet
api_secret = api_secret_testnet if testnet else api_secret_mainnet

# SELECTED URL
api_url = "https://api-testnet.bybit.com" if testnet else "https://api.bybit.com"
ws_public_url = "wss://stream-testnet.bybit.com/v5/public/linear" if testnet else "wss://stream.bybit.com/v5/public/linear"

# SESSION Activation
session_public = HTTP(testnet=testnet)
session_private = HTTP(testnet=testnet, api_key=api_key, api_secret=api_secret)

limit_order_basis = True  # will ensure positions (except for Close) will be placed on limit basis. CHANGE IT TO FALSE FOR PLACING MARKET ORDERS

# Updated code for fetching wallet balance with accountType specified
try:
    # balance = session_private.get_wallet_balance(category="linear", accountType="UNIFIED")  # Specify accountType
    # print(balance)
    # # Extract the available balance for USDT from the API response
    # tradeable_capital_usdt = float(balance['result']['list'][0]['coin'][0]['walletBalance'])  # Adjust according to the API response structure
    tradeable_capital_usdt = 250  # Adjust based on available equity as per you
except Exception as e:
    print(f"Error retrieving wallet balance: {e}")

# Define other variables
stop_loss_fail_safe = 0.08   #For now I have taken SL as 8%, you can change it According to your risk appetite
signal_trigger_thresh = 2.5  # z-score threshold which determines trade (must be above zero), MODIFY IT USING YOUR OWN PERSONAL BACKTESTING AND FORWARDTESTING

timeframe = 60
kline_limit = 200
z_score_window = 21
