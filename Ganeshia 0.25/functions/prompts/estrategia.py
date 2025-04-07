from functions.estrategias import analyze_limit_strategies, analyze_best_strategy, analyze_stop_limit_strategies, analyze_stop_strategies

def selecionar_estrategia(acao):
    symbol = "WINZ24"
    if acao in ['buy', 'sell']:
        estrategia = analyze_best_strategy(symbol)
    elif acao in ['buy_limit', 'sell_limit']:
        estrategia = analyze_limit_strategies(symbol)
    elif acao in ['buy_stop', 'sell_stop']:
        estrategia = analyze_stop_strategies(symbol)
    elif acao in ['buy_stop_limit', 'sell_stop_limit']:
        estrategia = analyze_stop_limit_strategies(symbol)
    else:
        estrategia = "Estratégia não definida"
    
    return estrategia
