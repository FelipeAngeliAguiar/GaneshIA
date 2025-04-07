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

# Estratégia baseada em cruzamento de médias móveis para ordens `buy_limit`
def buy_limit_sma_strategy(data, short_window=5, long_window=20):
    data['SMA_short'] = data['close'].rolling(window=short_window).mean()
    data['SMA_long'] = data['close'].rolling(window=long_window).mean()

    # Sinal de compra: quando SMA curta cruza acima da SMA longa (tendência de alta)
    data['Signal'] = np.where(data['SMA_short'] > data['SMA_long'], 1.0, 0.0)
    
    # Identifica mudanças na posição (0 -> 1 indica cruzamento de compra)
    data['Position'] = data['Signal'].diff()

    # Sinaliza uma ordem buy_limit abaixo do preço atual (retração)
    buy_limit_price = data['close'].iloc[-1] * 0.99  # Exemplo: 1% abaixo do preço atual
    
    return data, buy_limit_price

# Estratégia baseada em Bollinger Bands para ordens `sell_limit`
def sell_limit_bollinger_strategy(data, window=20, no_of_std=2):
    data['SMA'] = data['close'].rolling(window=window).mean()
    data['STD'] = data['close'].rolling(window=window).std()

    # Calcula as bandas de Bollinger
    data['Upper Band'] = data['SMA'] + (data['STD'] * no_of_std)
    data['Lower Band'] = data['SMA'] - (data['STD'] * no_of_std)

    # Sinal de venda: quando o preço atinge a banda superior (sobrecompra)
    data['Signal'] = np.where(data['close'] >= data['Upper Band'], -1.0, 0.0)
    
    # Identifica mudanças na posição (0 -> -1 indica um sinal de venda)
    data['Position'] = data['Signal'].diff()

    # Sinaliza uma ordem sell_limit acima do preço atual (retração)
    sell_limit_price = data['close'].iloc[-1] * 1.01  # Exemplo: 1% acima do preço atual
    
    return data, sell_limit_price

# Estratégia baseada no RSI para ordens `buy_limit`
def buy_limit_rsi_strategy(data, period=14, rsi_threshold=30):
    delta = data['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # Sinal de compra: RSI abaixo de rsi_threshold (exemplo: 30)
    data['Signal'] = np.where(data['RSI'] < rsi_threshold, 1.0, 0.0)
    
    # Identifica mudanças na posição (0 -> 1 indica condição de compra)
    data['Position'] = data['Signal'].diff()

    # Sinaliza uma ordem buy_limit abaixo do preço atual
    buy_limit_price = data['close'].iloc[-1] * 0.98  # Exemplo: 2% abaixo do preço atual
    
    return data, buy_limit_price

# Estratégia baseada no Momentum Oscillator para ordens `sell_limit`
def sell_limit_momentum_strategy(data, period=10, momentum_threshold=1.05):
    data['Momentum'] = data['close'] / data['close'].shift(period)
    
    # Sinal de venda: Momentum Oscillator acima do limite (exemplo: 1.05)
    data['Signal'] = np.where(data['Momentum'] > momentum_threshold, -1.0, 0.0)
    
    # Identifica mudanças na posição (0 -> -1 indica condição de venda)
    data['Position'] = data['Signal'].diff()

    # Sinaliza uma ordem sell_limit acima do preço atual
    sell_limit_price = data['close'].iloc[-1] * 1.02  # Exemplo: 2% acima do preço atual
    
    return data, sell_limit_price

def candlestick_reversal_limit_strategy(data):
    # Identificação de Doji e Hammer
    data['Doji'] = np.abs(data['open'] - data['close']) < (data['high'] - data['low']) * 0.1
    data['Hammer'] = (data['close'] > data['open']) & ((data['high'] - data['close']) <= (data['close'] - data['low']) * 0.3)

    # Buy limit com Hammer e Sell limit com Doji
    buy_limit_price = data['close'].iloc[-1] * 0.99 if data['Hammer'].iloc[-1] else None
    sell_limit_price = data['close'].iloc[-1] * 1.01 if data['Doji'].iloc[-1] else None
    
    return data, buy_limit_price, sell_limit_price

def buy_limit_vwap_strategy(data):
    data['VWAP'] = (data['close'] * data['tick_volume']).cumsum() / data['tick_volume'].cumsum()

    # Buy limit próximo ao VWAP, se preço atual estiver acima
    buy_limit_price = data['VWAP'].iloc[-1] * 0.99 if data['close'].iloc[-1] > data['VWAP'].iloc[-1] else None
    
    return data, buy_limit_price

def analyze_limit_strategies(symbol):
    data = get_market_data(symbol)
    if data is None or data.empty:
        print(f"No data available for {symbol}")
        return None

    # Estratégias focadas em ordens pendentes de compra e venda limite
    strategies = {
        "Buy Limit SMA": buy_limit_sma_strategy,
        "Sell Limit Bollinger": sell_limit_bollinger_strategy,
        "Buy Limit RSI": buy_limit_rsi_strategy,
        "Sell Limit Momentum": sell_limit_momentum_strategy,
        "Candlestick Reversal Limit": candlestick_reversal_limit_strategy,
        "Buy Limit VWAP": buy_limit_vwap_strategy
    }

    results = {}

    # Calcula as estratégias e armazena os preços de limite sugeridos
    for strategy_name, strategy_func in strategies.items():
        strategy_data = data.copy()
        if strategy_name == "Candlestick Reversal Limit":
            _, buy_limit_price, sell_limit_price = strategy_func(strategy_data)
            results[f"{strategy_name} Buy Limit"] = buy_limit_price
            results[f"{strategy_name} Sell Limit"] = sell_limit_price
        else:
            _, limit_price = strategy_func(strategy_data)
            results[strategy_name] = limit_price

    return results
