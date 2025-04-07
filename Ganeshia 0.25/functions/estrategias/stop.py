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

# Estratégia de rompimento para ordens `buy_stop` com base no rompimento de alta (SMA)
def buy_stop_breakout_strategy(data, short_window=5, long_window=20):
    data['SMA_short'] = data['close'].rolling(window=short_window).mean()
    data['SMA_long'] = data['close'].rolling(window=long_window).mean()

    # Sinal de compra: quando a SMA curta cruza acima da SMA longa
    data['Signal'] = np.where(data['SMA_short'] > data['SMA_long'], 1.0, 0.0)
    
    # Identifica mudanças na posição (0 -> 1 indica cruzamento de compra)
    data['Position'] = data['Signal'].diff()

    # Sinaliza uma ordem buy_stop acima do preço atual (rompimento)
    buy_stop_price = data['close'].iloc[-1] * 1.01  # Exemplo: 1% acima do preço atual
    
    return data, buy_stop_price

# Estratégia de rompimento para ordens `sell_stop` com base no rompimento de baixa (SMA)
def sell_stop_breakout_strategy(data, short_window=5, long_window=20):
    data['SMA_short'] = data['close'].rolling(window=short_window).mean()
    data['SMA_long'] = data['close'].rolling(window=long_window).mean()

    # Sinal de venda: quando a SMA curta cruza abaixo da SMA longa (tendência de baixa)
    data['Signal'] = np.where(data['SMA_short'] < data['SMA_long'], -1.0, 0.0)
    
    # Identifica mudanças na posição (0 -> -1 indica cruzamento de venda)
    data['Position'] = data['Signal'].diff()

    # Sinaliza uma ordem sell_stop abaixo do preço atual (rompimento)
    sell_stop_price = data['close'].iloc[-1] * 0.99  # Exemplo: 1% abaixo do preço atual
    
    return data, sell_stop_price

# Estratégia baseada no RSI para ordens `buy_stop`
def buy_stop_rsi_strategy(data, period=14, rsi_threshold=70):
    delta = data['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # Sinal de compra: RSI acima de rsi_threshold (exemplo: 70)
    data['Signal'] = np.where(data['RSI'] > rsi_threshold, 1.0, 0.0)
    
    # Identifica mudanças na posição (0 -> 1 indica condição de compra)
    data['Position'] = data['Signal'].diff()

    # Sinaliza uma ordem buy_stop acima do preço atual (rompimento de alta)
    buy_stop_price = data['close'].iloc[-1] * 1.02  # Exemplo: 2% acima do preço atual
    
    return data, buy_stop_price

# Estratégia baseada no ATR para ordens `sell_stop`
def sell_stop_atr_volatility_strategy(data, period=14, multiplier=1.5):
    data['High-Low'] = data['high'] - data['low']
    data['High-Close'] = np.abs(data['high'] - data['close'].shift(1))
    data['Low-Close'] = np.abs(data['low'] - data['close'].shift(1))

    # True Range é o máximo entre High-Low, High-Close, Low-Close
    data['True Range'] = data[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)

    # ATR (Average True Range) é a média do True Range
    data['ATR'] = data['True Range'].rolling(window=period).mean()

    # Sinal de venda: se o preço cair abaixo do valor atual menos ATR * multiplier
    sell_stop_price = data['close'].iloc[-1] - (data['ATR'].iloc[-1] * multiplier)
    
    return data, sell_stop_price

def bollinger_band_strategy(data, period=20, deviation=2):
    data['MA'] = data['close'].rolling(window=period).mean()
    data['Upper'] = data['MA'] + (data['close'].rolling(window=period).std() * deviation)
    data['Lower'] = data['MA'] - (data['close'].rolling(window=period).std() * deviation)

    # Identifica condições de reversão para buy_stop e sell_stop
    buy_stop_price = data['Upper'].iloc[-1]  # Exemplo: Banda Superior
    sell_stop_price = data['Lower'].iloc[-1]  # Exemplo: Banda Inferior
    
    return data, buy_stop_price, sell_stop_price

def candlestick_reversal_strategy(data):
    data['Hammer'] = (data['close'] > data['open']) & ((data['high'] - data['close']) <= (data['close'] - data['low']) * 0.3)
    data['ShootingStar'] = (data['open'] > data['close']) & ((data['high'] - data['open']) >= (data['open'] - data['low']) * 0.3)
    
    # Buy stop quando encontramos "Hammer"; sell stop para "Shooting Star"
    buy_stop_price = data['high'].iloc[-1] * 1.01 if data['Hammer'].iloc[-1] else None
    sell_stop_price = data['low'].iloc[-1] * 0.99 if data['ShootingStar'].iloc[-1] else None
    
    return data, buy_stop_price, sell_stop_price

def analyze_stop_strategies(symbol):
    data = get_market_data(symbol)
    if data is None or data.empty:
        print(f"No data available for {symbol}")
        return None

    # Estratégias focadas em ordens pendentes de compra e venda stop
    strategies = {
        "Buy Stop Breakout": buy_stop_breakout_strategy,
        "Sell Stop Breakout": sell_stop_breakout_strategy,
        "Buy Stop RSI": buy_stop_rsi_strategy,
        "Sell Stop ATR Volatility": sell_stop_atr_volatility_strategy
    }

    results = {}

    # Calcula as estratégias e armazena os preços de stop sugeridos
    for strategy_name, strategy_func in strategies.items():
        strategy_data, stop_price = strategy_func(data.copy())
        results[strategy_name] = stop_price

    return results
