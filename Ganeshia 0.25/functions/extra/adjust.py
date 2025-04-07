def adjust_take_profit(current_price, take_profit, order_type):
    """
    Ajusta o Take Profit (TP) com base no tipo de operação (compra/venda) e na diferença máxima de 500 pontos.

    :param current_price: Preço atual do ativo.
    :param take_profit: Valor do Take Profit a ser ajustado.
    :param order_type: Tipo da ordem ('compra' ou 'venda').
    :return: Novo valor do Take Profit ajustado.
    """
    # Verificar os valores antes do cálculo
    print(f"Tipo de ordem: {order_type}")
    print(f"Preço atual: {current_price}, TP original: {take_profit}")
    
    point_difference = abs(take_profit - current_price)
    print(f"Diferença de pontos calculada: {point_difference}")

    # Se a diferença for maior que 500 pontos, ajusta para 500 pontos
    if point_difference > 500:
        if order_type == 'compra':
            # Ajusta TP para exatamente 500 pontos acima do preço atual em caso de compra
            take_profit = current_price + 500
        elif order_type == 'venda':
            # Ajusta TP para exatamente 500 pontos abaixo do preço atual em caso de venda
            take_profit = current_price - 500

    print(f"Novo valor de TP ajustado: {take_profit}")
    
    return take_profit
