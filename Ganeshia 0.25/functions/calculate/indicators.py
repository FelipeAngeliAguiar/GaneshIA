def calculate_indicators(data):
    data['MA_7'] = data['close'].rolling(window=7).mean()
    data['MA_22'] = data['close'].rolling(window=22).mean()
    data['MA_99'] = data['close'].rolling(window=99).mean()
    data['MACD'] = data['MA_7'] - data['MA_22']
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data
