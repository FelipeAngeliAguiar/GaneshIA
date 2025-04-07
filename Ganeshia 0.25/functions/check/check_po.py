import MetaTrader5 as mt5

def check_pending_orders(symbol):
    """
    Verifica se há ordens pendentes para o símbolo e retorna True se a ordem foi ativada.
    """
    # Obter todas as ordens pendentes no MetaTrader 5
    orders = mt5.orders_get(symbol=symbol)

    if orders is None or len(orders) == 0:
        print("Nenhuma ordem pendente encontrada.")
        return False

    # Exibir ordens pendentes e verificar status
    for order in orders:
        print(f"Ordem pendente encontrada: ID {order.ticket}, Preço de Ativação: {order.price}")
        # Verifica o status da ordem, se foi executada ou ainda está pendente
        if order.type in (mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_SELL_STOP) and order.state == mt5.ORDER_STATE_PLACED:
            print(f"Ordem pendente {order.ticket} ainda não foi ativada.")
            return False  # Ordem ainda não ativada

    print("Ordem pendente ativada ou nenhuma ordem pendente.")
    return True  # Ordem foi ativada ou removida
