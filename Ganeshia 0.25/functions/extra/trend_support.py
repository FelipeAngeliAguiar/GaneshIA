import pandas as pd
from datetime import datetime, timedelta

# Exemplo de como converter o índice para datetime se necessário
def preprocess_data(data):
    if not pd.api.types.is_datetime64_any_dtype(data.index):
        data.index = pd.to_datetime(data.index)
    return data

def analyze_trend_and_support(data):
    # Preprocessar os dados para garantir que o índice seja do tipo datetime
    data = preprocess_data(data)
    
    # Verificar se 'close' está nas colunas
    if 'close' not in data.columns:
        print("Colunas disponíveis no DataFrame:", data.columns)
        raise KeyError("A coluna 'close' não foi encontrada no DataFrame.")
    
    end_time = data.index[-1]
    
    # Definindo os períodos para análise de tendências
    primary_start_time = end_time - timedelta(days=30)  # Tendência primária (1 mês)
    secondary_start_time = end_time - timedelta(days=7)  # Tendência secundária (1 semana)
    tertiary_start_time = end_time - timedelta(days=1)  # Tendência terciária (1 dia)
    
    # Extraindo os dados para cada período
    primary_data = data.loc[primary_start_time:end_time]
    secondary_data = data.loc[secondary_start_time:end_time]
    tertiary_data = data.loc[tertiary_start_time:end_time]
    
    # Função para determinar a tendência
    def determine_trend(data_period):
        if data_period['close'].iloc[-1] > data_period['close'].iloc[0]:
            return "alta"
        elif data_period['close'].iloc[-1] < data_period['close'].iloc[0]:
            return "baixa"
        else:
            return "lateralizada"
    
    # Determinando as tendências
    primary_trend = determine_trend(primary_data)
    secondary_trend = determine_trend(secondary_data)
    tertiary_trend = determine_trend(tertiary_data)
    
    # Determinando suporte e resistência a partir do período mais recente (terciária)
    high = tertiary_data['high'].max()
    low = tertiary_data['low'].min()

    # Extraindo múltiplos suportes e resistências (máximo e mínimo de cada período)
    primary_high = primary_data['high'].max()
    primary_low = primary_data['low'].min()
    secondary_high = secondary_data['high'].max()
    secondary_low = secondary_data['low'].min()

    # Calculando os níveis de Fibonacci
    from functions.calculate import calculate_fibonacci_retracement
    fibonacci_levels = calculate_fibonacci_retracement(high, low)
    
    # Organizando os três suportes
    supports = sorted([low, primary_low, secondary_low], reverse=True)
    resistances = sorted([high, primary_high, secondary_high], reverse=True)

    return {
        'primary_trend': primary_trend,
        'secondary_trend': secondary_trend,
        'tertiary_trend': tertiary_trend,
        'supports': supports[:3],  # Os três maiores níveis de suporte
        'resistances': resistances[:3],  # Os três maiores níveis de resistência
        'fibonacci_levels': fibonacci_levels
    }
