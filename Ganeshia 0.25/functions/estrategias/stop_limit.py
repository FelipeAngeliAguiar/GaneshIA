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

# Estratégia de stop limit com base no rompimento de alta usando Bollinger Bands
def buy_stop_limit_bollinger_strategy(data, window=20, no_of_std=2):
    data['SMA'] = data['close'].rolling(window=window).mean()
    data['STD'] = data['close'].rolling(window=window).std()

    # Calcula as bandas de Bollinger
    data['Upper Band'] = data['SMA'] + (data['STD'] * no_of_std)
    data['Lower Band'] = data['SMA'] - (data['STD'] * no_of_std)

    # Condição para compra: rompimento da banda superior
    data['Signal'] = np.where(data['close'] > data['Upper Band'], 1.0, 0.0)
    data['Position'] = data['Signal'].diff()

    # Definir o preço de ativação e o preço limite
    buy_stop_price = data['Upper Band'].iloc[-1]  # Ativação acima da banda superior
    buy_limit_price = buy_stop_price * 1.005  # Preço limite um pouco acima do preço de ativação (exemplo: 0.5% acima)

    return data, buy_stop_price, buy_limit_price

def candlestick_reversal_stop_limit_strategy(data):
    # Detecta padrões de Martelo e Estrela Cadente
    data['Hammer'] = (data['close'] > data['open']) & ((data['high'] - data['close']) <= (data['close'] - data['low']) * 0.3)
    data['ShootingStar'] = (data['open'] > data['close']) & ((data['high'] - data['open']) >= (data['open'] - data['low']) * 0.3)

    # Definir preços para buy_stop_limit com Martelo e sell_stop_limit com Estrela Cadente
    buy_stop_price = data['high'].iloc[-1] * 1.01 if data['Hammer'].iloc[-1] else None
    buy_limit_price = buy_stop_price * 1.003 if buy_stop_price else None
    sell_stop_price = data['low'].iloc[-1] * 0.99 if data['ShootingStar'].iloc[-1] else None
    sell_limit_price = sell_stop_price * 0.997 if sell_stop_price else None

    return data, buy_stop_price, buy_limit_price, sell_stop_price, sell_limit_price

def buy_stop_limit_momentum_strategy(data, period=10, momentum_threshold=1.03):
    data['Momentum'] = data['close'] / data['close'].shift(period)
    
    # Definir preço de ativação e limite com base no rompimento de momentum
    buy_stop_price = data['close'].iloc[-1] * 1.01 if data['Momentum'].iloc[-1] > momentum_threshold else None
    buy_limit_price = buy_stop_price * 1.003 if buy_stop_price else None
    
    return data, buy_stop_price, buy_limit_price

# Estratégia de stop limit com base na reversão de baixa usando EMA
def sell_stop_limit_ema_strategy(data, short_window=9, long_window=26):
    data['EMA_short'] = data['close'].ewm(span=short_window, adjust=False).mean()
    data['EMA_long'] = data['close'].ewm(span=long_window, adjust=False).mean()

    # Condição para venda: quando a EMA curta cruza abaixo da EMA longa
    data['Signal'] = np.where(data['EMA_short'] < data['EMA_long'], -1.0, 0.0)
    data['Position'] = data['Signal'].diff()

    # Definir o preço de ativação e o preço limite
    sell_stop_price = data['close'].iloc[-1] * 0.99  # Exemplo de preço de ativação 1% abaixo do preço atual
    sell_limit_price = sell_stop_price * 0.995  # Preço limite 0.5% abaixo do preço de ativação

    return data, sell_stop_price, sell_limit_price

# Estratégia de stop limit com base no RSI para ordens de compra
def buy_stop_limit_rsi_strategy(data, period=14, rsi_threshold=70):
    delta = data['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # Sinal de compra: RSI acima de rsi_threshold (exemplo: 70)
    data['Signal'] = np.where(data['RSI'] > rsi_threshold, 1.0, 0.0)
    data['Position'] = data['Signal'].diff()

    # Preço de ativação e limite para buy_stop_limit
    buy_stop_price = data['close'].iloc[-1] * 1.01  # Exemplo: ativação 1% acima do preço atual
    buy_limit_price = buy_stop_price * 1.005  # Exemplo: preço limite 0.5% acima do preço de ativação
    
    return data, buy_stop_price, buy_limit_price

# Estratégia de stop limit com base no ATR para ordens de venda
def sell_stop_limit_atr_strategy(data, period=14, multiplier=1.5):
    data['High-Low'] = data['high'] - data['low']
    data['High-Close'] = np.abs(data['high'] - data['close'].shift(1))
    data['Low-Close'] = np.abs(data['low'] - data['close'].shift(1))

    # True Range é o máximo entre High-Low, High-Close, Low-Close
    data['True Range'] = data[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)

    # ATR (Average True Range) é a média do True Range
    data['ATR'] = data['True Range'].rolling(window=period).mean()

    # Preço de ativação e limite para sell_stop_limit
    sell_stop_price = data['close'].iloc[-1] - (data['ATR'].iloc[-1] * multiplier)
    sell_limit_price = sell_stop_price * 0.995  # Exemplo: 0.5% abaixo do preço de ativação
    
    return data, sell_stop_price, sell_limit_price

def analyze_stop_limit_strategies(symbol):
    data = get_market_data(symbol)
    if data is None or data.empty:
        print(f"No data available for {symbol}")
        return None

    # Estratégias focadas em ordens stop limit de compra e venda
    strategies = {
        "Buy Stop Limit Bollinger": buy_stop_limit_bollinger_strategy,
        "Sell Stop Limit EMA": sell_stop_limit_ema_strategy,
        "Buy Stop Limit RSI": buy_stop_limit_rsi_strategy,
        "Sell Stop Limit ATR": sell_stop_limit_atr_strategy,
        "Candlestick Reversal Stop Limit": candlestick_reversal_stop_limit_strategy,
        "Buy Stop Limit Momentum": buy_stop_limit_momentum_strategy
    }

    results = {}

    # Calcula as estratégias e armazena os preços de stop e limite sugeridos
    for strategy_name, strategy_func in strategies.items():
        strategy_data = data.copy()
        if strategy_name == "Candlestick Reversal Stop Limit":
            _, buy_stop_price, buy_limit_price, sell_stop_price, sell_limit_price = strategy_func(strategy_data)
            results[f"{strategy_name} Buy Stop"] = {'Stop Price': buy_stop_price, 'Limit Price': buy_limit_price}
            results[f"{strategy_name} Sell Stop"] = {'Stop Price': sell_stop_price, 'Limit Price': sell_limit_price}
        else:
            _, stop_price, limit_price = strategy_func(strategy_data)
            results[strategy_name] = {'Stop Price': stop_price, 'Limit Price': limit_price}
    
    return results
