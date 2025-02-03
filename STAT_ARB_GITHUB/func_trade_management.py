from config_execution_api import signal_positive_ticker
from config_execution_api import signal_negative_ticker
from config_execution_api import signal_trigger_thresh
from config_execution_api import tradeable_capital_usdt
from config_execution_api import limit_order_basis
from config_execution_api import session_private
from func_price_calls import get_ticker_trade_liquidity
from func_get_zscore import get_latest_zscore
from func_execution_calls import initialise_order_execution, set_stop_loss  # ADDED set_stop_loss
from func_order_review import check_order
import time

def manage_new_trades(kill_switch):
    order_long_id = ""
    order_short_id = ""
    signal_side = ""
    hot = False
    stop_loss_long = 0  # ADDED: Track stop loss for long
    stop_loss_short = 0  # ADDED: Track stop loss for short

    zscore, signal_sign_positive = get_latest_zscore()

    if abs(zscore) > signal_trigger_thresh:
        hot = True
        print("-- Trade Status HOT --")
        print("-- Placing and Monitoring Existing Trades --")

    if hot and kill_switch == 0:
        avg_liquidity_ticker_p, last_price_p = get_ticker_trade_liquidity(signal_positive_ticker)
        avg_liquidity_ticker_n, last_price_n = get_ticker_trade_liquidity(signal_negative_ticker)

        if signal_sign_positive:
            long_ticker = signal_positive_ticker
            short_ticker = signal_negative_ticker
            avg_liquidity_long = avg_liquidity_ticker_p
            avg_liquidity_short = avg_liquidity_ticker_n
            last_price_long = last_price_p
            last_price_short = last_price_n
        else:
            long_ticker = signal_negative_ticker
            short_ticker = signal_positive_ticker
            avg_liquidity_long = avg_liquidity_ticker_n
            avg_liquidity_short = avg_liquidity_ticker_p
            last_price_long = last_price_n
            last_price_short = last_price_p

        capital_long = tradeable_capital_usdt * 0.5
        capital_short = tradeable_capital_usdt - capital_long
        initial_fill_target_long_usdt = avg_liquidity_long * last_price_long
        initial_fill_target_short_usdt = avg_liquidity_short * last_price_short
        initial_capital_injection_usdt = min(initial_fill_target_long_usdt, initial_fill_target_short_usdt)

        if limit_order_basis:
            initial_capital_usdt = capital_long if initial_capital_injection_usdt > capital_long else initial_capital_injection_usdt
        else:
            initial_capital_usdt = capital_long

        remaining_capital_long = capital_long
        remaining_capital_short = capital_short
        print(remaining_capital_long, remaining_capital_short, initial_capital_usdt)

        order_status_long = ""
        order_status_short = ""
        counts_long = 0
        counts_short = 0

        while kill_switch == 0:
            # ==================================================================
            # ADDED: Capture stop loss values when placing orders
            # ==================================================================
            if counts_long == 0:
                order_long_id, stop_loss_long = initialise_order_execution(long_ticker, "Long", initial_capital_usdt)  # MODIFIED
                counts_long = 1 if order_long_id else 0
                remaining_capital_long -= initial_capital_usdt

            if counts_short == 0:
                order_short_id, stop_loss_short = initialise_order_execution(short_ticker, "Short", initial_capital_usdt)  # MODIFIED
                counts_short = 1 if order_short_id else 0
                remaining_capital_short -= initial_capital_usdt

            if zscore > 0:
                signal_side = "positive"
            else:
                signal_side = "negative"

            # ==================================================================
            # ADDED: Set stop loss after market orders execute
            # ==================================================================
            if not limit_order_basis and counts_long and counts_short:
                kill_switch = 1
                time.sleep(5)  # Wait for orders to fill
                # Set stop losses for both positions
                set_stop_loss(long_ticker, "Buy",stop_loss_long)
                set_stop_loss(short_ticker, "Sell",stop_loss_short)

            time.sleep(3)

            zscore_new, signal_sign_p_new = get_latest_zscore()
            if kill_switch == 0:
                if abs(zscore_new) > signal_trigger_thresh * 0.9 and signal_sign_p_new == signal_sign_positive:
                    if counts_long == 1:
                        order_status_long = check_order(long_ticker, order_long_id, remaining_capital_long, "Long")
                    if counts_short == 1:
                        order_status_short = check_order(short_ticker, order_short_id, remaining_capital_short, "Short")
                    print(order_status_long, order_status_short, zscore_new)

                    if order_status_long == "Order Active" or order_status_short == "Order Active":
                        continue
                    if order_status_long == "Partial Fill" or order_status_short == "Partial Fill":
                        continue
                    if order_status_long == "Trade Complete" and order_status_short == "Trade Complete":
                        kill_switch = 1
                    if order_status_long == "Position Filled" and order_status_short == "Position Filled":
                        counts_long = 0
                        counts_short = 0
                    if order_status_long == "Try Again":
                        counts_long = 0
                    if order_status_short == "Try Again":
                        counts_short = 0
                else:
                    session_private.cancel_all_orders(category="linear", symbol=signal_positive_ticker)
                    session_private.cancel_all_orders(category="linear", symbol=signal_negative_ticker)
                    kill_switch = 1

    return kill_switch, signal_side
