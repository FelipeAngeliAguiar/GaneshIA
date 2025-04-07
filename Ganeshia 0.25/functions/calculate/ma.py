def calculate_moving_averages(data, ma_periods=[7, 22, 50]):
    if 'close' not in data.columns:
        raise ValueError("O DataFrame precisa conter a coluna 'close' para calcular as médias móveis.")
    
    # Verifica se os períodos são válidos (maiores que 0 e menores que o tamanho do DataFrame)
    for period in ma_periods:
        if not isinstance(period, int) or period <= 0:
            raise ValueError(f"Período inválido: {period}. Os períodos devem ser números inteiros positivos.")
        if period > len(data):
            print(f"Atenção: Período {period} excede o número de linhas disponíveis no DataFrame. Será ignorado.")
            continue

        # Calcula e adiciona as médias móveis ao DataFrame para cada período
        ma_column_name = f'MA_{period}'
        data[ma_column_name] = data['close'].rolling(window=period).mean()
    
    return data
