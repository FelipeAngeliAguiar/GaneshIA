import pandas as pd

def calculate_bollinger_bands(data, window=20, no_of_std=2):
    if 'close' not in data.columns:
        raise ValueError("A coluna 'close' é necessária para calcular as Bandas de Bollinger.")
    
    # Calcula a Média Móvel Simples (SMA)
    data['SMA'] = data['close'].rolling(window=window).mean()
    
    # Calcula o desvio padrão do preço de fechamento
    data['STD'] = data['close'].rolling(window=window).std()
    
    # Calcula as Bandas de Bollinger
    data['Upper_Band'] = data['SMA'] + (no_of_std * data['STD'])
    data['Lower_Band'] = data['SMA'] - (no_of_std * data['STD'])
    
    # Retorna apenas as colunas relevantes
    return data[['Upper_Band', 'Lower_Band']]


