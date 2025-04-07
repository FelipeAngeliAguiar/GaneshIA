import pandas as pd

def calculate_adx(data, period=14):
    # Calcula o directional movement (DM) positivo e negativo
    plus_dm = data['high'].diff()
    minus_dm = data['low'].diff()

    # Filtra os valores negativos para plus_dm e positivos para minus_dm
    plus_dm = plus_dm.where(plus_dm > 0, 0)
    minus_dm = minus_dm.where(minus_dm < 0, 0).abs()

    # Calcula o True Range (TR) com três métodos diferentes e pega o máximo deles
    tr1 = data['high'] - data['low']
    tr2 = abs(data['high'] - data['close'].shift(1))
    tr3 = abs(data['low'] - data['close'].shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Calcula o Average True Range (ATR)
    atr = tr.rolling(window=period).mean()

    # Calcula os directional indices (DI) positivo e negativo
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

    # Calcula o DX (Directional Movement Index)
    dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100

    # Calcula o ADX (Average Directional Index)
    adx = dx.rolling(window=period).mean()

    return adx
