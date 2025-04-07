from .support import check_support_resistance_levels
from .trend_reversal import check_trend_reversal
from .bollinger import check_bollinger_condition  
from .volume import check_average_volume_condition     
from .ema import check_ema_condition
from .candles import check_candlestick_patterns

def verify_conditions(data, last_price, supports, resistances, operacao_atual):
    # Inicialização das variáveis de condição
    trend_reversal = "Não atendida"
    bollinger_condition = "Não atendida"
    support_resistance = "Não atendida"
    volume_condition = "Não atendida"
    ema_condition = "Não atendida"
    candlestick_condition = "Não atendida"
    candlestick_patterns = []

    if not isinstance(operacao_atual, dict):
        print("Erro: operacao_atual precisa ser um dicionário.")
        return None, False, []
    
    # Obter o tipo de operação atual
    tipo_operacao_atual = operacao_atual.get("Tipo de Operação", "desconhecido")

    # Verificação de reversão de tendência
    try:
        trend_reversal_result = check_trend_reversal(data)
        if trend_reversal_result == "reversão para compra":
            trend_reversal = "Atendido p/ Alta"
        elif trend_reversal_result == "reversão para venda":
            trend_reversal = "Atendido p/ Baixa"
    except ValueError as e:
        print(f"Erro ao verificar reversão de tendência: {e}")

    # Verificação das Bollinger Bands
    try:
        bollinger_result = check_bollinger_condition(data)
        if bollinger_result == "upper_band":
            bollinger_condition = "Atendido p/ Alta"
        elif bollinger_result == "lower_band":
            bollinger_condition = "Atendido p/ Baixa"
    except Exception as e:
        print(f"Erro ao verificar condição de Bollinger Bands: {e}")

    # Verificação de suporte/resistência
    try:
        support_resistance_result, level = check_support_resistance_levels(last_price, supports, resistances)
        if support_resistance_result == "Próximo ao suporte":
            support_resistance = "Atendido p/ Alta"
        elif support_resistance_result == "Próximo à resistência":
            support_resistance = "Atendido p/ Baixa"
    except Exception as e:
        print(f"Erro ao verificar suporte/resistência: {e}")

    # Verificação do volume médio
    try:
        volume_result = check_average_volume_condition(data)
        if volume_result == "above_average":
            volume_condition = "Atendido p/ Alta"
        elif volume_result == "below_average":
            volume_condition = "Atendido p/ Baixa"
    except Exception as e:
        print(f"Erro ao verificar condição de volume médio: {e}")

    # Verificação de condição da EMA
    try:
        ema_condition_result = check_ema_condition(data, period=9)
        if ema_condition_result == "ema_up":
            ema_condition = "Atendido p/ Alta"
        elif ema_condition_result == "ema_down":
            ema_condition = "Atendido p/ Baixa"
    except Exception as e:
        print(f"Erro ao verificar condição da EMA: {e}")

    # Verificação de padrões de candlestick
    try:
        candlestick_condition, candlestick_patterns = check_candlestick_patterns(data)
    except Exception as e:
        print(f"Erro ao verificar padrões de candlestick: {e}")

    # Criar um dicionário com todas as condições e seus estados
    conditions = {
        'tendencia': trend_reversal,
        'bollinger_bands': bollinger_condition,
        'support_resistance': support_resistance,
        'volume': volume_condition,
        'ema_9': ema_condition,
        'candlestick': candlestick_condition
    }

    # Lista de mensagens explicativas
    messages = []
    if tipo_operacao_atual == "sell":
        if all(cond == "Atendido p/ Baixa" for cond in conditions.values() if cond != "Não atendida"):
            messages.append("Continuidade da operação de venda prevista.")
        elif any(cond == "Atendido p/ Alta" for cond in conditions.values()):
            messages.append("Possível reversão para compra detectada.")
    elif tipo_operacao_atual == "buy":
        if all(cond == "Atendido p/ Alta" for cond in conditions.values() if cond != "Não atendida"):
            messages.append("Continuidade da operação de compra prevista.")
        elif any(cond == "Atendido p/ Baixa" for cond in conditions.values()):
            messages.append("Possível reversão para venda detectada.")
    else:
        messages.append("Tipo de operação desconhecido. Não é possível prever continuidade ou reversão.")

    if "próximo à banda superior" in bollinger_condition:
        messages.append("Alta volatilidade próxima à banda superior das Bollinger Bands, possível continuação de alta.")
    elif "próximo à banda inferior" in bollinger_condition:
        messages.append("Alta volatilidade próxima à banda inferior das Bollinger Bands, possível continuação de baixa.")

    if candlestick_patterns:
        messages.append(f"Padrões de Candlestick identificados: {', '.join(candlestick_patterns)}")

    if all(cond == "Não atendida" for cond in conditions.values()):
        messages.append("Mercado lateral detectado, sem sinais claros de tendência.")

    # Retornar conditions, is_ready, e lista de mensagens
    is_ready = sum(1 for condition in conditions.values() if condition != "Não atendida") >= 3
    return conditions, is_ready, messages
