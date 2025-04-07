import pandas as pd
import MetaTrader5 as mt5
import numpy as np  
from functions.calculate import calculate_moving_averages, calculate_macd, calculate_rsi, calculate_adx, calculate_bollinger_bands

def get_data(symbol, interval, num_candles):
    # Inicializa a conexão com o MetaTrader 5
    if not mt5.initialize():
        print("Falha ao inicializar o MetaTrader 5")
        return None

    # Verifica se o intervalo é uma constante de timeframe válida do MetaTrader 5
    if interval not in [mt5.TIMEFRAME_M1, mt5.TIMEFRAME_M5, mt5.TIMEFRAME_H1]:
        print("Intervalo não suportado")
        return None

    # Obtém os dados históricos das candles
    rates = mt5.copy_rates_from_pos(symbol, interval, 0, num_candles)

    # Verifica se a obtenção dos dados foi bem-sucedida
    if rates is None or len(rates) == 0:
        print(f"Falha ao obter dados para o símbolo: {symbol}")
        return None

    # Converte os dados para um DataFrame do pandas
    data = pd.DataFrame(rates)
    
    # Converte timestamps para o formato datetime
    data['time'] = pd.to_datetime(data['time'], unit='s')

    # Renomeia as colunas para serem consistentes
    data.rename(columns={
        'open': 'open', 
        'close': 'close', 
        'high': 'high', 
        'low': 'low', 
        'tick_volume': 'tick_volume'}, inplace=True)

    # Adiciona atributos para o símbolo, intervalo e número de candles
    data.attrs['symbol'] = symbol
    data.attrs['interval'] = interval
    data.attrs['num_candles'] = num_candles

    # Calcula as médias móveis e adiciona ao DataFrame
    data = calculate_moving_averages(data)
    
    # Calcula o MACD e a Linha de Sinal
    macd_data = calculate_macd(data)
    data['MACD'] = macd_data['MACD']
    data['Signal Line'] = macd_data['Signal Line']

    # Calcula o RSI e adiciona ao DataFrame
    data = calculate_rsi(data)
    
    # Calcula o ADX e adiciona ao DataFrame
    data['ADX'] = calculate_adx(data)
    
    # Calcula as Bandas de Bollinger e adiciona ao DataFrame
    bollinger_data = calculate_bollinger_bands(data)
    data['Upper_Band'] = bollinger_data['Upper_Band']
    data['Lower_Band'] = bollinger_data['Lower_Band']
    
    # Calcula a média de volume (Volume_Mean) e adiciona ao DataFrame
    data['Volume_Mean'] = data['tick_volume'].rolling(window=20).mean()

   # Arredonda os valores para zero casas decimais e converte para inteiros
    columns_to_round = [
        'MA_7', 'MA_22', 'MA_50',  # Trocamos 'MA_99' por 'MA_50'
        'MACD', 'Signal Line', 
        'RSI', 'ADX', 
        'SMA', 'STD', 
        'Upper_Band', 'Lower_Band', 
        'Volume_Mean'
    ]

    # Preenche NaN com 0 (ou outro valor que faça sentido no seu contexto)
    data[columns_to_round] = data[columns_to_round].fillna(0)

    # Remove valores infinitos (caso existam)
    data[columns_to_round] = data[columns_to_round].replace([np.inf, -np.inf], 0)

    # Arredondar e converter para inteiro
    data[columns_to_round] = data[columns_to_round].round(0).astype(int)

    # Verifica se todos os cálculos foram feitos corretamente
    missing_columns = [col for col in columns_to_round if col not in data.columns]
    if missing_columns:
        print(f"Faltando colunas: {', '.join(missing_columns)}")

    return data  # Retorna o DataFrame completo para mais cálculos
