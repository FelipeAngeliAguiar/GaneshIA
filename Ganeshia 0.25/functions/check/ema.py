def calculate_ema(data, period=9, column='close'):
    """Calcula a Média Móvel Exponencial (EMA) para reduzir o ruído dos dados."""
    return data[column].ewm(span=period, adjust=False).mean()

def check_ema_condition(data, period=9):
    """Verifica se o preço está acima ou abaixo da EMA para indicar tendência."""
    ema = calculate_ema(data, period)
    close_price = data['close'].iloc[-1]
    
    if close_price > ema.iloc[-1]:
        return "ema_up"
    elif close_price < ema.iloc[-1]:
        return "ema_down"
    
    return "ema_flat"
