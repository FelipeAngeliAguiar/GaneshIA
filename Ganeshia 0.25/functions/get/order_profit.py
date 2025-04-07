import MetaTrader5 as mt5

def get_order_profit(ticket):
    position = mt5.positions_get(ticket=ticket)
    if position:
        profit = position[0].profit
        return profit
    else:
        print("Erro ao obter a posição.")
        return 0.0
