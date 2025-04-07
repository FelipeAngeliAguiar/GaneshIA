def check_trend_reversal(data):

    # Verifique se todas as colunas necessárias estão presentes
    required_columns = ['MA_7', 'MA_22', 'MA_50', 'MACD']  # Trocamos 'MA_99' por 'MA_50'
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        raise ValueError(f"Colunas ausentes no DataFrame: {', '.join(missing_columns)}")

    # Verifica se o DataFrame contém pelo menos uma linha
    if data.empty:
        raise ValueError("O DataFrame está vazio.")
        
    ma_7 = data['MA_7'].iloc[-1]
    ma_22 = data['MA_22'].iloc[-1]
    ma_50 = data['MA_50'].iloc[-1]  # Trocamos 'MA_99' por 'MA_50'
    macd = data['MACD'].iloc[-1]

    # Remove o uso do RSI

    # Verifica as condições de reversão
    if ma_7 < ma_22 < ma_50 and macd < 0:  # Trocamos 'MA_99' por 'MA_50' e removemos RSI
        
        return "reversão para venda"
    elif ma_7 > ma_22 > ma_50 and macd > 0:  # Trocamos 'MA_99' por 'MA_50' e removemos RSI
        
        return "reversão para compra"
    
    
    return None
