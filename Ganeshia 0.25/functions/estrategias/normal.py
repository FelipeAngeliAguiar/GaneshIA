import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def connect_mt5():
    if not mt5.initialize():
        print("Failed to initialize MT5")
        return False
    return True

def get_market_data(symbol, timeframe=mt5.TIMEFRAME_M1, num_candles=500):
    utc_from = datetime.now() - timedelta(minutes=num_candles)
    rates = mt5.copy_rates_from(symbol, timeframe, utc_from, num_candles)
    if rates is None:
        print(f"Failed to get rates for {symbol}")
        return None
    return pd.DataFrame(rates)

def sma_crossover_strategy(data, short_window=5, long_window=20):
    data['SMA_short'] = data['close'].rolling(window=short_window).mean()
    data['SMA_long'] = data['close'].rolling(window=long_window).mean()
    data['Signal'] = 0.0
    data.loc[short_window:, 'Signal'] = np.where(data['SMA_short'][short_window:] > data['SMA_long'][short_window:], 1.0, 0.0)
    data['Position'] = data['Signal'].diff()
    return data

def ema_crossover_strategy(data, short_window=5, long_window=20):
    data['EMA_short'] = data['close'].ewm(span=short_window, adjust=False).mean()
    data['EMA_long'] = data['close'].ewm(span=long_window, adjust=False).mean()
    data['Signal'] = 0.0
    data.loc[short_window:, 'Signal'] = np.where(data['EMA_short'][short_window:] > data['EMA_long'][short_window:], 1.0, 0.0)
    data['Position'] = data['Signal'].diff()
    return data

def rsi_strategy(data, window=14, overbought=70, oversold=30):
    delta = data['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    data['Signal'] = np.where(data['RSI'] > overbought, -1.0, np.where(data['RSI'] < oversold, 1.0, 0.0))
    data['Position'] = data['Signal'].diff()
    return data

def bollinger_bands_strategy(data, window=20, no_of_std=2):
    data['SMA'] = data['close'].rolling(window=window).mean()
    data['STD'] = data['close'].rolling(window=window).std()
    data['Upper Band'] = data['SMA'] + (data['STD'] * no_of_std)
    data['Lower Band'] = data['SMA'] - (data['STD'] * no_of_std)
    data['Signal'] = np.where(data['close'] > data['Upper Band'], -1.0, np.where(data['close'] < data['Lower Band'], 1.0, 0.0))
    data['Position'] = data['Signal'].diff()
    return data

def macd_strategy(data, short_window=12, long_window=26, signal_window=9):
    data['EMA_short'] = data['close'].ewm(span=short_window, adjust=False).mean()
    data['EMA_long'] = data['close'].ewm(span=long_window, adjust=False).mean()
    data['MACD'] = data['EMA_short'] - data['EMA_long']
    data['Signal_Line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()
    data['Signal'] = np.where(data['MACD'] > data['Signal_Line'], 1.0, 0.0)
    data['Position'] = data['Signal'].diff()
    return data

def vwap_strategy(data):
    data['Cumulative TPV'] = (data['close'] * data['tick_volume']).cumsum()
    data['Cumulative Volume'] = data['tick_volume'].cumsum()
    data['VWAP'] = data['Cumulative TPV'] / data['Cumulative Volume']
    data['Signal'] = np.where(data['close'] > data['VWAP'], 1.0, -1.0)
    data['Position'] = data['Signal'].diff()
    return data

def analyze_best_strategy(symbol):
    data = get_market_data(symbol)
    if data is None or data.empty:
        print(f"No data available for {symbol}")
        return None

    # Lista de estratégias com foco em day trade
    strategies = {
        "SMA Crossover": sma_crossover_strategy,
        "EMA Crossover": ema_crossover_strategy,
        "RSI": rsi_strategy,
        "Bollinger Bands": bollinger_bands_strategy,
        "MACD": macd_strategy,
        "VWAP": vwap_strategy,
    }

    results = {}

    # Calcula o lucro de cada estratégia
    for strategy_name, strategy_func in strategies.items():
        strategy_data = strategy_func(data.copy())
        profit = (strategy_data['Position'] * strategy_data['close'].diff()).sum()
        results[strategy_name] = profit

    # Identifica a melhor estratégia com base no lucro
    best_strategy = max(results, key=results.get)

    return best_strategy
