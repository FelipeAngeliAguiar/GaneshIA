import MetaTrader5 as mt5
from functions.ml import registrar_abertura_operacao
from datetime import datetime, timedelta

def round_to_nearest_5(value):
    """Arredonda o valor para o número mais próximo divisível por 5."""
    return round(value / 5) * 5

def ensure_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        print(f"Erro ao converter o valor '{value}' para float.")
        return None

def adjust_sl_tp(stop_price, stop_loss, take_profit, action, point, digits):
    """Ajusta o SL e TP se forem menores que 1000, somando/subtraindo ao preço de ativação."""
    if stop_loss is not None and stop_loss < 10000:
        if action.lower() == "buy_stop":
            stop_loss = stop_price - stop_loss * point
        else:
            stop_loss = stop_price + stop_loss * point
    
    if take_profit is not None and take_profit < 10000:
        if action.lower() == "buy_stop":
            take_profit = stop_price + take_profit * point
        else:
            take_profit = stop_price - take_profit * point
    
    # Arredondar SL e TP conforme precisão do ativo
    stop_loss = round(stop_loss, digits)
    take_profit = round(take_profit, digits)
    
    return stop_loss, take_profit

def validate_prices(price_trigger, stop_loss, take_profit, current_price, action):
    """Valida se os preços de ativação, SL e TP são coerentes com o preço de mercado."""
    if action.lower() == "sell_stop":
        if price_trigger >= current_price:
            print(f"Erro: Preço de ativação {price_trigger} deve ser menor que o preço de mercado {current_price} para sell_stop.")
            return False
        if stop_loss <= price_trigger or take_profit >= price_trigger:
            print(f"Erro: SL ({stop_loss}) deve ser maior e TP ({take_profit}) deve ser menor que o preço de ativação ({price_trigger}) para sell_stop.")
            return False
    elif action.lower() == "buy_stop":
        if price_trigger <= current_price:
            print(f"Erro: Preço de ativação {price_trigger} deve ser maior que o preço de mercado {current_price} para buy_stop.")
            return False
        if stop_loss >= price_trigger or take_profit <= price_trigger:
            print(f"Erro: SL ({stop_loss}) deve ser menor e TP ({take_profit}) deve ser maior que o preço de ativação ({price_trigger}) para buy_stop.")
            return False
    return True

def place_stop_order(account_info, symbol, action, price_trigger, stop_loss, take_profit, response_explanation, condicoes_mercado, usuario, volume):
    """Função para colocar ordens stop de compra ou venda."""
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Símbolo {symbol} não encontrado.")
        return

    stop_loss = ensure_float(stop_loss)
    take_profit = ensure_float(take_profit)
    price_trigger = ensure_float(price_trigger)
    volume = ensure_float(volume)

    if volume is None or volume <= 0:
        print(f"Volume inválido: {volume}")
        return

    if isinstance(usuario, set):
        usuario = list(usuario)[0] 

    if not isinstance(usuario, str):
        print(f"Erro: `usuario` deveria ser uma string, mas recebeu: {type(usuario)}")
        return

    if not isinstance(condicoes_mercado, dict):
        print(f"Erro: 'condicoes_mercado' deveria ser um dicionário, mas recebeu {type(condicoes_mercado)}")
        return

    point = symbol_info.point
    digits = symbol_info.digits
    stop_loss, take_profit = adjust_sl_tp(price_trigger, stop_loss, take_profit, action, point, digits)
    
    price_trigger = round(price_trigger, digits)
    price_trigger = ensure_float(price_trigger)

    current_price = symbol_info.bid if action.lower() == "sell_stop" else symbol_info.ask
    print(f"Preço de mercado atual: {current_price}")

    if not validate_prices(price_trigger, stop_loss, take_profit, current_price, action):
        print(f"Erro: preços inválidos para a ordem {action}.")
        return

    order_type = mt5.ORDER_TYPE_BUY_STOP if action.lower() == "buy_stop" else mt5.ORDER_TYPE_SELL_STOP

    print(f"Informações da conta: {account_info}\n"
          f"Símbolo: {symbol}\n"
          f"Ação: {action}\n"
          f"Preço de ativação: {price_trigger}\n"
          f"Parada de perda: {stop_loss}\n"
          f"Pegar lucro: {take_profit}\n"
          f"Resposta de explicação: {response_explanation}\n"
          f"Condições do mercado: {condicoes_mercado}\n"
          f"Usuário: {usuario}\n"
          f"Volume: {volume}\n")
    
    deviation = 200 

    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price_trigger,  
        "sl": stop_loss,  
        "tp": take_profit,  
        "deviation": deviation,  
        "magic": 123456,
        "comment": "Ordem Stop",
        "type_time": mt5.ORDER_TIME_DAY,  
        "type_filling": mt5.ORDER_FILLING_RETURN,  
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
            print(f"Ordem de {action} registrada no banco de dados para {symbol_info.name} com preço de abertura: {price_trigger:.5f} e id_position: {id_position}")
        except Exception as e:
            print(f"Erro ao registrar a ordem no banco de dados: {str(e)}")
