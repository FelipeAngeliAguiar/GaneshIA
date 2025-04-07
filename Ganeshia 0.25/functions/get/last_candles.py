import logging
import pandas as pd

def get_last_candle_data(data):
    """
    Extrai os dados da última vela no DataFrame e retorna um dicionário com as colunas relevantes.
    Trata colunas ausentes com valores padrão (None) e valores NaN com None.
    """
    # Colunas esperadas
    required_columns = ['close', 'high', 'low']
    
    # Verificar quais colunas estão faltando
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        logging.warning(f"Colunas ausentes no DataFrame: {', '.join(missing_columns)}")
    
    # Verificar se o DataFrame tem pelo menos uma linha
    if data.empty:
        logging.error("O DataFrame está vazio.")
        raise ValueError("O DataFrame está vazio.")
    
    # Extrair a última linha do DataFrame
    last_candle = data.iloc[-1]
    
    # Criar o dicionário com valores padrão para colunas ausentes e tratar NaN como None
    candle_data = {
        "CLOSE": last_candle['close'] if 'close' in data.columns and pd.notna(last_candle['close']) else None,
        "HIGH": last_candle['high'] if 'high' in data.columns and pd.notna(last_candle['high']) else None,
        "LOW": last_candle['low'] if 'low' in data.columns and pd.notna(last_candle['low']) else None
    }
    

    return candle_data
