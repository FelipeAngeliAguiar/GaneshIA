import MetaTrader5 as mt5

def has_open_trade(symbol):
    """
    Verifica se há operações abertas para o símbolo no MetaTrader 5.
    """
    open_positions = mt5.positions_get(symbol=symbol)
    
    if open_positions is None:
        print(f"Erro ao verificar posições abertas para {symbol}, código do erro:", mt5.last_error())
        return False
    
    # Se houver pelo menos uma operação aberta, retorna True
    return len(open_positions) > 0
