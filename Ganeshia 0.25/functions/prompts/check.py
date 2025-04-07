import MetaTrader5 as mt5
from datetime import datetime, timedelta

def get_last_trade_info(symbol):
    """
    Obtém as informações da última operação aberta no histórico.
    Retorna Take Profit (tp), Stop Loss (sl), Preço de Abertura (open_price), e Tipo de Operação (type).
    """
    # Inicializa o MetaTrader 5
    if not mt5.initialize():
        print("Falha ao inicializar o MetaTrader 5")
        return None

    # Pega o histórico de negociações das últimas 24 horas
    now = datetime.now()
    from_date = now - timedelta(days=1)
    trades = mt5.history_deals_get(from_date, now)

    if trades is None:
        print(f"Nenhuma transação encontrada para o símbolo {symbol}")
        return None

    # Encontra a última operação para o símbolo
    for trade in reversed(trades):
        if trade.symbol == symbol and trade.type in [mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_SELL]:
            trade_info = {
                'type': 'buy' if trade.type == mt5.ORDER_TYPE_BUY else 'sell',
                'open_price': trade.price,
                'sl': getattr(trade, 'sl', None),  # Usa getattr para evitar erro se o atributo não existir
                'tp': getattr(trade, 'tp', None)   # Usa getattr para evitar erro se o atributo não existir
            }
            return trade_info

    return None

def gerar_prompt_gpt(trade_info, conditions, messages):
    """
    Gera o prompt para o GPT com as informações da operação atual e as condições do mercado.
    O GPT deve responder se deve "manter" ou "fechar" a operação com um nível de certeza baseado em sinais de reversão.
    """
    if trade_info is None:
        return "Erro: Não foi possível obter informações da última operação."

    tp = trade_info['tp']
    sl = trade_info['sl']
    open_price = trade_info['open_price']
    operation_type = trade_info['type']
    
    # Adicionar mensagens de condição no prompt
    messages_text = "\n".join(f"- {msg}" for msg in messages)
    
    prompt = (
        f"Situação atual da operação no símbolo:\n"
        f"Tipo de operação: {operation_type}\n"
        f"Preço de Abertura: {open_price}\n"
        f"Take Profit: {tp}\n"
        f"Stop Loss: {sl}\n"
        f"\nCondições de Mercado:\n"
        f"Tendência: {conditions['tendencia']}\n"
        f"Bollinger Bands: {conditions['bollinger_bands']}\n"
        f"Suporte/Resistência: {conditions['support_resistance']}\n"
        f"Volume Médio: {conditions['volume']}\n"
        f"Padrões de Candlestick: {conditions['candlestick']}\n"
        f"EMA(9): {conditions['ema_9']}\n"
        f"\n**Resumo da Análise de Condições:**\n{messages_text}\n"
        f"\nAgora explique se a operação deve ser mantida ou fechada, considerando sinais claros de uma possível reversão.\n"
        f"A certeza deve ser expressa entre 0% e 100%, com base nas condições de mercado.\n\n"
        f"**IMPORTANTE**:\n"
        f"- Se houver sinais fortes de reversão e a certeza da análise for maior ou igual a 80%, escolha 'fechar'.\n"
        f"- Se os sinais de reversão forem incertos ou a certeza for menor que 80%, escolha 'manter'.\n"
        f"RESPONDA SOMENTE COM:\n"
        f"Ação: 'manter' ou 'fechar'\n"
        f"Certeza: número% (Exemplo: 80%)"
    )
    
    return prompt
