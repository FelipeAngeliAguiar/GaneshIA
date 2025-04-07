import logging
from candlestick_patterns import identify_candlestick_patterns
from functions.calculate import calculate_adx, calculate_macd
import pandas as pd

def check_adx_condition(data, threshold=20):
    """Verifica se o ADX está acima do limite para identificar força da tendência."""
    adx_series = calculate_adx(data)
    adx = adx_series.iloc[-1]
    return adx > threshold

import pandas as pd

def calculate_atr(data, period=14):
    """
    Calcula o Average True Range (ATR) para medir a volatilidade do ativo.

    Parâmetros:
    - data: DataFrame contendo as colunas 'high', 'low', e 'close'.
    - period: número de períodos para o cálculo do ATR (default=14).

    Retorna:
    - DataFrame com uma coluna adicional 'ATR' contendo o valor do ATR.
    """
    # Calcula as variações necessárias para o True Range (TR)
    high_low = data['high'] - data['low']
    high_close = (data['high'] - data['close'].shift()).abs()
    low_close = (data['low'] - data['close'].shift()).abs()
    
    # O True Range é o maior valor entre high_low, high_close e low_close
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Calcula o ATR como uma média móvel do True Range
    data['ATR'] = true_range.rolling(window=period).mean()
    
    return data


def check_trend_condition(data):
    """Verifica a tendência com base em três médias móveis."""
    required_columns = ['MA_7', 'MA_22', 'MA_50', 'MACD']  
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        raise ValueError(f"Colunas ausentes no DataFrame: {', '.join(missing_columns)}")

    if data.empty:
        raise ValueError("O DataFrame está vazio.")

    ma_7 = data['MA_7'].iloc[-1]
    ma_22 = data['MA_22'].iloc[-1]
    ma_50 = data['MA_50'].iloc[-1]  
    macd = data['MACD'].iloc[-1]

    if ma_7 < ma_22 < ma_50 and macd < 0:
        return "Atendida p/ Baixa"
    elif ma_7 > ma_22 > ma_50 and macd > 0:
        return "Atendida p/ Alta"
    else:
        return "Não atendida"

def check_macd_condition(data):
    """Verifica se o MACD está acima ou abaixo da linha de sinal para indicar alta ou baixa."""
    macd_data = calculate_macd(data)
    macd = macd_data['MACD'].iloc[-1]
    signal_line = macd_data['Signal Line'].iloc[-1]
    
    # Ajuste para garantir que a condição seja atendida quando macd > signal_line
    if macd > signal_line:
        return "Atendido p/ Alta"
    elif macd < signal_line:
        return "Atendido p/ Baixa"
    else:
        return "Não atendida"

def check_bollinger_condition(data, atr_threshold=1.0):
    if 'ATR' not in data.columns:
        data = calculate_atr(data)
        
    close_price = data['close'].iloc[-1]
    upper_band = data['Upper_Band'].iloc[-1]
    lower_band = data['Lower_Band'].iloc[-1]
    sma_5 = data['close'].rolling(window=5).mean().iloc[-1]
    band_distance = upper_band - lower_band

    # Condição ajustada para considerar alta ou baixa próximo às bandas
    if close_price >= upper_band - (band_distance * 0.1):
        return "Atendido p/ Alta (próximo à banda superior)"
    elif close_price <= lower_band + (band_distance * 0.1):
        return "Atendido p/ Baixa (próximo à banda inferior)"
    else:
        return "Não atendida"

def check_volume_condition(data):
    """Adapta a condição para considerar volumes abaixo da média como 'Atendido p/ Baixa'."""
    volume = data['tick_volume'].iloc[-1]
    volume_mean = data['Volume_Mean'].iloc[-1]

    # Ajuste para aceitar volumes baixos como condição válida para Baixa
    if volume > volume_mean:
        return "Atendido p/ Alta"
    elif volume < volume_mean:
        return "Atendido p/ Baixa"
    else:
        return "Não atendida"

def check_candlestick_patterns(data):
    patterns = identify_candlestick_patterns(data)
    
    alta_patterns = [
        "Bullish Engulfing", "Hammer", "Inverted Hammer", "Morning Star", 
        "Three White Soldiers", "Piercing Line", "Three Inside Up", 
        "Tweezer Bottom", "Bullish Harami", "Dragonfly Doji", 
        "Bullish Belt Hold", "Rising Three Methods", "Bullish Abandoned Baby"
    ]
    
    baixa_patterns = [
        "Bearish Engulfing", "Shooting Star", "Evening Star", 
        "Three Black Crows", "Dark Cloud Cover", "Three Inside Down", 
        "Tweezer Top", "Hanging Man", "Bearish Harami", "Gravestone Doji", 
        "Bearish Belt Hold", "Falling Three Methods", "Bearish Abandoned Baby"
    ]
    
    is_alta = any(pattern in alta_patterns for pattern in patterns)
    is_baixa = any(pattern in baixa_patterns for pattern in patterns)
    
    if is_alta:
        return "Atendida p/ Alta", patterns
    elif is_baixa:
        return "Atendida p/ Baixa", patterns
    
    return "Não atendida", patterns

def calculate_support_resistance(data):
    """Simula cálculo de suporte e resistência para análise de pontos de reversão."""
    recent_low = data['low'].rolling(window=20).min().iloc[-1]
    recent_high = data['high'].rolling(window=20).max().iloc[-1]
    return recent_low, recent_high

def check_market_conditions(data):
    # Verificação individual de cada condição
    trend_condition = check_trend_condition(data) or "Não atendida"
    macd_condition = check_macd_condition(data) or "Não atendida"
    bollinger_condition = check_bollinger_condition(data) or "Não atendida"
    volume_condition = check_volume_condition(data) or "Não atendida"
    candlestick_condition, candlestick_patterns = check_candlestick_patterns(data)
    
    # Dicionário com o status de cada condição
    conditions_met = {
        'tendencia': trend_condition,
        'macd': macd_condition,
        'bollinger_bands': bollinger_condition,
        'volume': volume_condition,
        'candlestick': candlestick_condition
    }
    
    # Identificar condições atendidas e não atendidas
    attended_conditions = {name: cond for name, cond in conditions_met.items() if "Atendida" in cond or "Atendido" in cond}
    attended_conditions_count = len(attended_conditions)
    ready = attended_conditions_count >= 4  # Defina prontidão com base nas condições atendidas

    support, resistance = calculate_support_resistance(data)
    messages = []  # Lista de mensagens para diferentes condições

    # Adiciona mensagens baseadas nas condições atendidas
    if all(cond == "Atendida p/ Alta" or cond == "Atendido p/ Alta" for cond in attended_conditions.values()):
        messages.append(f"Continuidade de alta até resistência em {resistance}")
    elif all(cond == "Atendida p/ Baixa" or cond == "Atendido p/ Baixa" for cond in attended_conditions.values()):
        messages.append(f"Continuidade de baixa até suporte em {support}")
    if "Alta" in candlestick_condition:
        messages.append(f"Possível reversão para alta próximo ao suporte em {support} (Padrões: {candlestick_patterns})")
    if "Baixa" in candlestick_condition:
        messages.append(f"Possível reversão para baixa próximo à resistência em {resistance} (Padrões: {candlestick_patterns})")
    if "próximo à banda superior" in bollinger_condition:
        messages.append("Alta volatilidade próxima à banda superior das Bollinger Bands, possível continuação de alta")
    if "próximo à banda inferior" in bollinger_condition:
        messages.append("Alta volatilidade próxima à banda inferior das Bollinger Bands, possível continuação de baixa")
    if attended_conditions_count == 0:
        messages.append("Baixa volatilidade e ausência de sinais de tendência (mercado lateral)")

    # Caso não haja mensagens específicas, use uma mensagem genérica
    if not messages:
        messages.append("Condições mistas, sem uma direção clara")

    # Mensagem detalhada com todas as condições atendidas e não atendidas
    details_message = (
        f"Condições atendidas ({attended_conditions_count}/5): {', '.join(attended_conditions.keys())}\n"
        f"Condições não atendidas: {', '.join(key for key in conditions_met if key not in attended_conditions)}"
    )

    return "\n".join(messages), ready, conditions_met, details_message
