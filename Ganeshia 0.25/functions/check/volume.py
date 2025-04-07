def check_average_volume_condition(data):
    """
    Verifica se o volume atual está acima ou abaixo da média de volume.
    :param data: DataFrame contendo a coluna 'tick_volume' com o volume de cada candle.
    :return: 'above_average' se o volume estiver acima da média,
             'below_average' se o volume estiver abaixo da média.
    """
    volume = data['tick_volume']
    volume_mean = volume.rolling(window=20).mean()
    
    # Verificar se o volume atual está acima ou abaixo da média
    current_volume = volume.iloc[-1]
    if current_volume > volume_mean.iloc[-1]:
        return "above_average"  # Volume acima da média, indicando pressão de alta
    elif current_volume < volume_mean.iloc[-1]:
        return "below_average"  # Volume abaixo da média, indicando pressão de baixa
    else:
        return "average"  # Volume na média, sem pressão clara