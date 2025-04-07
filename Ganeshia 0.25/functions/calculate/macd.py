def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    # Verifique se a coluna 'close' existe e contém dados suficientes
    if 'close' not in data.columns or data['close'].isnull().all():
        raise ValueError("Coluna 'close' não encontrada ou contém apenas valores nulos.")
    
    if len(data) < long_window:
        raise ValueError(f"Dados insuficientes para calcular MACD. O DataFrame deve conter pelo menos {long_window} linhas.")
    
    # Fazer uma cópia dos dados para evitar modificações no DataFrame original
    data = data.copy()
    
    # Calcular as EMAs
    ema_short = data['close'].ewm(span=short_window, adjust=False).mean()
    ema_long = data['close'].ewm(span=long_window, adjust=False).mean()
    
    # Calcular o MACD e a Linha de Sinal
    macd = ema_short - ema_long
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    
    # Preencher valores NaN com 0 (evitar valores nulos)
    macd = macd.fillna(0)
    signal_line = signal_line.fillna(0)
    
    # Atribuir os valores calculados ao DataFrame
    data['MACD'] = macd
    data['Signal Line'] = signal_line
    
    return data[['MACD', 'Signal Line']]  # Retornar apenas as colunas relevantes
