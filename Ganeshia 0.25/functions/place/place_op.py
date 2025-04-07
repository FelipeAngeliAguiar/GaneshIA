import MetaTrader5 as mt5
from functions.ml import registrar_abertura_operacao
from datetime import datetime

def ensure_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        print(f"Erro ao converter o valor '{value}' para float.")
        return None

def adjust_sl_tp(current_price, stop_loss, take_profit, action, point):
    """
    Ajusta o Stop Loss (SL) e Take Profit (TP) para ordens buy e sell padrão.
    O SL e TP devem ser ajustados em relação ao preço de mercado atual.
    """
    # Ajustar Stop Loss
    if stop_loss is not None and stop_loss < 10000:  # Se SL for menor que 10000, ajustamos
        if action.lower() == "buy":
            stop_loss = current_price - stop_loss * point  # Para buy, o SL deve ser abaixo do preço atual
        else:
            stop_loss = current_price + stop_loss * point  # Para sell, o SL deve ser acima do preço atual

    # Ajustar Take Profit
    if take_profit is not None and take_profit < 10000:  # Se TP for menor que 10000, ajustamos
        if action.lower() == "buy":
            take_profit = current_price + take_profit * point  # Para buy, o TP deve ser acima do preço atual
        else:
            take_profit = current_price - take_profit * point  # Para sell, o TP deve ser abaixo do preço atual

    return stop_loss, take_profit

def place_order(account_info, symbol, action, stop_loss, take_profit, justificativa, condicoes_mercado, usuario, volume):
    stop_loss = ensure_float(stop_loss)
    take_profit = ensure_float(take_profit)
    volume = ensure_float(volume)

    if stop_loss is None or take_profit is None or volume is None:
        print("Stop Loss, Take Profit ou Volume inválidos. A ordem não será enviada.")
        return

    if not mt5.initialize():
        print(f"Erro ao inicializar o MetaTrader 5: {mt5.last_error()}")
        return

    account_info_mt5 = mt5.account_info()
    if account_info_mt5 is None:
        print("Erro ao conectar à conta de negociação.")
        return

    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None or not symbol_info.visible:
        print(f"Erro: símbolo '{symbol}' não encontrado ou está desabilitado.")
        if not mt5.symbol_select(symbol, True):
            print(f"Erro ao habilitar o símbolo '{symbol}'.")
            return

    tick_info = mt5.symbol_info_tick(symbol)
    if tick_info is None:
        print(f"Erro: informações do tick não disponíveis para o símbolo '{symbol}'.")
        return

    # Obter o preço de mercado atual (ask para buy, bid para sell)
    current_price = tick_info.ask if action.lower() == "buy" else tick_info.bid

    # Calcula o tipo de ordem (buy ou sell)
    order_type = mt5.ORDER_TYPE_BUY if action.lower() == "buy" else mt5.ORDER_TYPE_SELL

    # Ajustar SL e TP com base no preço de mercado
    point = symbol_info.point
    stop_loss, take_profit = adjust_sl_tp(current_price, stop_loss, take_profit, action, point)

    print(f"Informações da conta: {account_info}\n"
          f"Símbolo: {symbol}\n"
          f"Ação: {action}\n"
          f"Parada de perda: {stop_loss}\n"
          f"Pegar lucro: {take_profit}\n"
          f"Resposta de explicação: {justificativa}\n"
          f"Condições do mercado: {condicoes_mercado}\n"
          f"Usuário: {usuario}\n"
          f"Volume: {volume}\n")

    # Prepara o pedido
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": current_price,
        "sl": stop_loss,
        "tp": take_profit,
        "deviation": 10,
        "magic": 123456,
        "comment": "Ordem",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Envia o pedido
    result = mt5.order_send(request)

    if result is None:
        print("Falha ao enviar a ordem:", mt5.last_error())
    elif result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Falha ao enviar a ordem: {result.retcode}, {result.comment}")
    else:
        print(f"Ordem enviada com sucesso na conta {account_info['nome']}")

        id_position = result.order
        usuario = account_info['nome']

        try:
            registrar_abertura_operacao(justificativa, id_position, condicoes_mercado, usuario, action)
            print(f"Ordem de {action} registrada no banco de dados para {symbol_info.name}")
        except Exception as e:
            print(f"Erro ao registrar a ordem no banco de dados: {str(e)}")
