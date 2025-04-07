import MetaTrader5 as mt5

def close_position(position, reason):
    from functions.get import get_order_profit
    
    # Ensure the symbol is selected
    if not mt5.symbol_select(position.symbol, True):
        print(f"Failed to select symbol {position.symbol}")
        return False

    # Determine the order type (closing the opposite type)
    order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    price = mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask

    # Ensure the price data is valid
    if price is None:
        print(f"Failed to retrieve price for symbol {position.symbol}")
        return False

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": order_type,
        "position": position.ticket,
        "price": price,
        "deviation": 20,
        "magic": 234000,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    # Log full result details
    if result is None:
        print("Order send failed, result is None")
        print("Error code:", mt5.last_error())
        return False

    print(f"Order send result: {result}")
    print(f"Retcode: {result.retcode}, Comment: {result.comment}, Request ID: {result.request_id}")

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to close position, retcode: {result.retcode}, comment: {result.comment}")
        return False

    # Get the profit of the closed position and update the total_profit
    global total_profit  # Declare total_profit as global to modify the global variable
    profit = get_order_profit(position.ticket)  # Obtain the profit of the closed position
    
    # Handle cases where profit retrieval fails
    if profit is None:
        print(f"Failed to retrieve profit for position {position.ticket}")
    else:
        total_profit += profit  # Accumulate profit in the global variable
        print(f"Position closed successfully: {reason}. Profit: {profit:.2f}, Total Accumulated Profit: {total_profit:.2f}")
    
    return True
