import MetaTrader5 as mt5
from functions.ml import registrar_abertura_operacao
from datetime import datetime

def round_to_nearest_5(value):
    """Arredonda o valor para o número mais próximo divisível por 5."""
    return round(value / 5) * 5

def ensure_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        print(f"Erro ao converter o valor '{value}' para float.")
        return None

def adjust_sl_tp(limit_price, stop_loss, take_profit, action, point, digits):
    """Ajusta o SL e TP se forem menores que 1000, somando/subtraindo ao preço limite."""
    if stop_loss is not None and stop_loss < 10000:
        if action.lower() == "buy_limit":
            stop_loss = limit_price - stop_loss * point
        else:
            stop_loss = limit_price + stop_loss * point
    
    if take_profit is not None and take_profit < 10000:
        if action.lower() == "buy_limit":
            take_profit = limit_price + take_profit * point
        else:
            take_profit = limit_price - take_profit * point

    # Arredondar SL e TP conforme precisão do ativo
    stop_loss = round(stop_loss, digits)
    take_profit = round(take_profit, digits)
    
    return stop_loss, take_profit

def place_limit_order(account_info, symbol, action, limit_price, stop_loss, take_profit, response_explanation, condicoes_mercado, usuario, volume):
    """Função para colocar ordens limitadas de compra ou venda, ajustando SL e TP se necessário."""
    symbol_info = mt5.symbol_info(symbol)

    if symbol_info is None:
        print(f"Símbolo {symbol} não encontrado.")
        return

    # Certificar que SL, TP, volume e preço limite sejam floats e estejam corretamente definidos
    stop_loss = ensure_float(stop_loss)
    take_profit = ensure_float(take_profit)
    limit_price = ensure_float(limit_price)
    volume = ensure_float(volume)

    if volume is None or volume <= 0:
        print(f"Volume inválido: {volume}")
        return

    # Validar tipo de `usuario`
    if isinstance(usuario, set):
        usuario = list(usuario)[0]
    if not isinstance(usuario, str):
        print(f"Erro: `usuario` deveria ser uma string, mas recebeu: {type(usuario)}")
        return

    # Validar `condicoes_mercado`
    if not isinstance(condicoes_mercado, dict):
        print(f"Erro: 'condicoes_mercado' deveria ser um dicionário, mas recebeu {type(condicoes_mercado)}")
        return

    # Ajuste de SL e TP conforme o ponto e a precisão
    point = symbol_info.point
    digits = symbol_info.digits
    stop_loss, take_profit = adjust_sl_tp(limit_price, stop_loss, take_profit, action, point, digits)

    # Arredondar o preço limite de acordo com a precisão do ativo
    limit_price = round(limit_price, digits)
    limit_price = ensure_float(limit_price)

    # Verificar o preço de mercado atual para validar o preço limite
    current_price = symbol_info.bid if action.lower() == "sell_limit" else symbol_info.ask
    print(f"Preço de mercado atual: {current_price}")

    if (action.lower() == "sell_limit" and limit_price <= current_price) or \
       (action.lower() == "buy_limit" and limit_price >= current_price):
        print(f"Erro: Preço limite {limit_price} inválido para a ação {action} com preço de mercado {current_price}.")
        return

    # Definir o tipo de ordem
    order_type = mt5.ORDER_TYPE_BUY_LIMIT if action.lower() == "buy_limit" else mt5.ORDER_TYPE_SELL_LIMIT

    # Exibir informações de debug antes de enviar a ordem
    print(f"Informações da conta: {account_info}\n"
          f"Símbolo: {symbol}\n"
          f"Ação: {action}\n"
          f"Preço limite: {limit_price}\n"
          f"Parada de perda: {stop_loss}\n"
          f"Pegar lucro: {take_profit}\n"
          f"Resposta de explicação: {response_explanation}\n"
          f"Condições do mercado: {condicoes_mercado}\n"
          f"Usuário: {usuario}\n"
          f"Volume: {volume}\n")
    
    # Configuração do pedido com maior desvio para volatilidade
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": limit_price,
        "sl": stop_loss,
        "tp": take_profit,
        "deviation": 100,
        "magic": 123456,
        "comment": "Ordem Limitada",
        "type_time": mt5.ORDER_TIME_DAY,
        "type_filling": mt5.ORDER_FILLING_FOK,
        "expiration": 0,
    }

    result = mt5.order_send(request)

    if result is None:
        print("Falha ao enviar a ordem:", mt5.last_error())
    elif result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Falha ao enviar a ordem: {result.retcode}, {result.comment}")
    else:
        print(f"Ordem enviada com sucesso na conta {account_info['nome']}")

        id_position = result.order

        try:
            registrar_abertura_operacao(response_explanation, id_position, condicoes_mercado, usuario, action)
            print(f"Ordem registrada no banco de dados para {symbol_info.name} com preço de abertura: {limit_price:.5f} e id_position: {id_position}")
        except Exception as e:
            print(f"Erro ao registrar a ordem no banco de dados: {str(e)}")
