def calculate_rsi(data, window=14):
    # Calculate the difference in closing prices
    delta = data['close'].diff(1)
    
    # Get gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate the rolling averages of gains and losses
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    # Calculate the Relative Strength (RS) and the RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Ensure that the RSI series has the same index as the original data
    # This ensures that the length matches
    rsi_filled = rsi.reindex(data.index).fillna(50)  # Reindex and fill NaN with neutral value
    
    # Return the full DataFrame with the 'RSI' column added
    data['RSI'] = rsi_filled
    return data