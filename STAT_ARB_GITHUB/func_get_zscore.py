from config_execution_api import session_public
from func_calculations import get_trade_details
from func_price_calls import get_latest_klines
from func_stats import calculate_metrics
from config_execution_api import ticker_1
from config_execution_api import ticker_2
 
# Get latest z-score
def get_latest_zscore():
 
    # Get latest asset orderbook prices and add dummy price for latest
    orderbook_1 = session_public.get_orderbook(
        category="linear",
        symbol=ticker_1,
    )
    mid_price_1, _, _, = get_trade_details(orderbook_1)
    orderbook_2 = session_public.get_orderbook(
        category="linear",
        symbol=ticker_2,
    )
    mid_price_2, _, _, = get_trade_details(orderbook_2)
 
    # Get latest price history
    series_1, series_2 = get_latest_klines()
 
 
 
    # Get z_score and confirm if hot
    if len(series_1) > 0 and len(series_2) > 0:
 
        # Replace last kline price with latest orderbook mid price
        series_1 = series_1[:-1]
        series_2 = series_2[:-1]
        series_1.append(mid_price_1)
        series_2.append(mid_price_2)
 
        # Get latest zscore
        _, zscore_list = calculate_metrics(series_1, series_2)
 
        zscore = zscore_list[-1]
        if zscore > 0:
            signal_sign_positive = True
        else:
            signal_sign_positive = False
 
        # Return output
        print(zscore, signal_sign_positive)
        return (zscore, signal_sign_positive)
 
    # Return output if not true
    return

get_latest_zscore