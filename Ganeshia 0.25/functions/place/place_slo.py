import MetaTrader5 as mt5
from datetime import datetime
from functions.ml import registrar_abertura_operacao

def round_to_nearest_5(value):
    """Arredonda o valor para o número mais próximo divisível por 5."""
    return round(value / 5) * 5

def ensure_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        print(f"Erro ao converter o valor '{value}' para float.")
        return None

def place_stop_limit_order(account_info, symbol, action, price_trigger, limit_price, stop_loss, take_profit, justificativa, condicoes_mercado, usuario, volume):
    if not isinstance(condicoes_mercado, dict):
        print(f"Ajustando 'condicoes_mercado' para um dicionário vazio, valor recebido: {condicoes_mercado}")
        condicoes_mercado = {}

    # Inicializa a conexão com o MetaTrader 5
    if not mt5.initialize():
        print(f"Erro ao inicializar o MetaTrader 5: {mt5.last_error()}")
        return

    # Verificar se o volume é um número válido
    volume = ensure_float(volume)
    symbol_info = mt5.symbol_info(symbol)

    if symbol_info is None:
        print(f"Erro: símbolo '{symbol}' não encontrado.")
        return

    # Verifica se o símbolo está visível e tenta habilitar se necessário
    if not symbol_info.visible:
        print(f"O símbolo '{symbol}' está desabilitado, tentando habilitar.")
        if not mt5.symbol_select(symbol, True):
            print(f"Erro ao habilitar o símbolo '{symbol}'.")
            return

    min_lot = symbol_info.volume_min
    print(f"Volume mínimo permitido para {symbol}: {min_lot}")

    # Ajusta o volume se for menor que o permitido ou não for múltiplo do lote mínimo
    if volume < min_lot:
        print(f"Ajustando o volume para o mínimo permitido: {min_lot}.")
        volume = min_lot

    if volume % min_lot != 0:
        print(f"O volume {volume} não é um múltiplo do lote mínimo {min_lot}.")
        return

    # Mapeia as ações para os tipos de ordens
    order_types = {
        "buy_stop_limit": mt5.ORDER_TYPE_BUY_STOP_LIMIT,
        "sell_stop_limit": mt5.ORDER_TYPE_SELL_STOP_LIMIT
    }

    # Verifica se a ação é válida
    order_type = order_types.get(action.lower())
    if order_type is None:
        print(f"Ação '{action}' inválida para ordens stop limit.")
        return
    
    # Ajustar preços conforme a precisão do ativo
    digits = symbol_info.digits
    limit_price = round(limit_price, digits)
    price_trigger = round(price_trigger, digits)
    stop_loss = round(stop_loss, digits) if stop_loss else None
    take_profit = round(take_profit, digits) if take_profit else None
    
    # Verificar preço de mercado para validar o preço de ativação e limite
    current_price = symbol_info.bid if action.lower() == "sell_stop_limit" else symbol_info.ask
    print(f"Preço de mercado atual: {current_price}")

    # Validar se o preço de ativação faz sentido
    if (action.lower() == "buy_stop_limit" and price_trigger <= current_price) or \
       (action.lower() == "sell_stop_limit" and price_trigger >= current_price):
        print(f"Erro: Preço de ativação {price_trigger} inválido para a ação {action} com preço de mercado {current_price}.")
        return

    # Validar se o preço limite está corretamente posicionado em relação ao preço de ativação
    if (action.lower() == "buy_stop_limit" and limit_price <= price_trigger) or \
       (action.lower() == "sell_stop_limit" and limit_price >= price_trigger):
        print(f"Erro: Preço limite {limit_price} inválido em relação ao preço de ativação {price_trigger} para a ação {action}.")
        return

    # Exibir informações de debug antes de enviar a ordem
    print(f"Informações da conta: {account_info}\n"
          f"Símbolo: {symbol}\n"
          f"Ação: {action}\n"
          f"Preço de ativação: {price_trigger}\n"
          f"Parada de perda: {stop_loss}\n"
          f"Pegar lucro: {take_profit}\n"
          f"Preço de ativação: {price_trigger}\n"
          f"Preço Limite: {limit_price}\n"
          f"Resposta de explicação: {justificativa}\n"
          f"Condições do mercado: {condicoes_mercado}\n"
          f"Usuário: {usuario}\n"
          f"Volume: {volume}\n")
    
    # Prepara o pedido de ordem stop limit
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price_trigger,   # Preço de ativação (trigger)
        "price_limit": limit_price,  # Preço limite da ordem
        "sl": stop_loss,         # Stop Loss
        "tp": take_profit,       # Take Profit
        "deviation": 100,        # Aumentar o desvio para maior flexibilidade
        "magic": 123456,
        "comment": "Ordem Pendente Stop Limit",
        "type_time": mt5.ORDER_TIME_DAY,  # Ordem válida até o final do dia
        "type_filling": mt5.ORDER_FILLING_FOK,
        "expiration": 0,         # Sem expiração definida
    }

    # Envia o pedido
    result = mt5.order_send(request)

    if result is None:
        print("Falha ao enviar a ordem:", mt5.last_error())
    elif result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Falha ao enviar a ordem: {result.retcode}, {result.comment}")
    else:
        print(f"Ordem pendente de {action} enviada com sucesso na conta {account_info['nome']}")

        id_position = result.order
        registrar_abertura_operacao(justificativa, id_position, condicoes_mercado, usuario, action)

        print(f"Ordem pendente de {action} registrada no arquivo JSON e no banco de dados para {symbol_info.name} com preço de ativação: {request['price']:.5f} e id_position: {id_position}")
