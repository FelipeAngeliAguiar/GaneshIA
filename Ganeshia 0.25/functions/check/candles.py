from candlestick_patterns import identify_candlestick_patterns

def check_candlestick_patterns(data):
    """
    Verifica se há padrões de candles identificados e categoriza como Alta ou Baixa.
    """
    patterns = identify_candlestick_patterns(data)
    
    # Lista completa de padrões de alta e baixa, incluindo padrões adicionais
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
    
    # Determina se o padrão é de alta ou baixa
    is_alta = any(pattern in alta_patterns for pattern in patterns)
    is_baixa = any(pattern in baixa_patterns for pattern in patterns)
    
    if is_alta:
        return "Atendido p/ Alta", patterns
    elif is_baixa:
        return "Atendido p/ Baixa", patterns
    return "Não atendida", patterns
