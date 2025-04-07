import pandas as pd

def calculate_atr(data, period=14):
    """
    Calcula o Average True Range (ATR) em um DataFrame com as colunas 'high', 'low', 'close'.
    
    Parâmetros:
    - data: DataFrame contendo as colunas 'high', 'low', e 'close'.
    - period: número de períodos para cálculo do ATR (default=14).
    
    Retorna:
    - DataFrame com coluna adicional 'ATR'.
    """
    high_low = data['high'] - data['low']
    high_close = (data['high'] - data['close'].shift()).abs()
    low_close = (data['low'] - data['close'].shift()).abs()
    
    # Calcula o true range
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Calcula o ATR como uma média móvel do true range
    data['ATR'] = true_range.rolling(window=period).mean()
    return data

def check_bollinger_condition(data, atr_threshold=1.5):
    """
    Verifica se o preço está perto da banda superior ou inferior das Bollinger Bands, com filtros adicionais
    para day trade usando volatilidade e médias móveis curtas.
    
    Parâmetros:
    - data: DataFrame contendo as colunas 'close', 'Upper_Band', 'Lower_Band' e 'ATR' (opcional).
    - atr_threshold: Multiplicador do ATR para confirmar rompimentos com volatilidade.
    
    Retorna:
    - String indicando condição de compra, venda, ou sem condições.
    """
    # Verifica se a coluna 'ATR' está presente, e calcula se não estiver
    if 'ATR' not in data.columns:
        data = calculate_atr(data)
        
    close_price = data['close'].iloc[-1]
    upper_band = data['Upper_Band'].iloc[-1]
    lower_band = data['Lower_Band'].iloc[-1]
    atr = data['ATR'].iloc[-1]
    sma_5 = data['close'].rolling(window=5).mean().iloc[-1]  # Média móvel de 5 períodos
    band_distance = upper_band - lower_band

    # Filtro de volatilidade: apenas considera se a distância entre bandas está acima do ATR ajustado
    if band_distance < atr * atr_threshold:
        return "Sem condição (baixa volatilidade)"

    # Verifica se o preço está próximo das bandas superior ou inferior
    if close_price >= upper_band and close_price > sma_5:
        return "Atendido p/ Alta (volatilidade alta)"
    elif close_price <= lower_band and close_price < sma_5:
        return "Atendido p/ Baixa (volatilidade alta)"
    else:
        return "Não atendida"