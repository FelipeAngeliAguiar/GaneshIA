import re
from typing import Tuple, Optional

def parse_trade_signal(content: str) -> Tuple[Optional[str], Optional[float], Optional[float], Optional[float], Optional[float]]:
    print("Conteúdo recebido para análise:")
    print(content)  # Imprimir o conteúdo recebido
    
    try:
        # Extrair a ação
        action_match = re.search(r'(?i)\b(ação):\s*(manter|buy_stop|sell_stop|buy_limit|sell_limit|buy|sell|buy_stop_limit|sell_stop_limit)', content)
        if not action_match:
            raise ValueError("Ação não encontrada no conteúdo.")

        action = action_match.group(2).lower()
        print(f"Ação encontrada: {action}")  # Imprimir a ação encontrada

        # Extrair Stop Loss e Take Profit
        sl_match = re.search(r'(?i)stop loss:\s*([\d.]+)', content)
        tp_match = re.search(r'(?i)take profit:\s*([\d.]+)', content)

        if not sl_match or not tp_match:
            raise ValueError("Stop Loss ou Take Profit não encontrado na resposta.")

        stop_loss_points = float(sl_match.group(1))
        take_profit_points = float(tp_match.group(1))

        print(f"Stop Loss: {stop_loss_points}, Take Profit: {take_profit_points}")  # Imprimir SL e TP

        # Inicializar variáveis para preço de ativação e preço limite
        price_trigger = None
        limit_price = None

        # Para ações do tipo Stop e Stop Limit, extrair tanto preço de ativação quanto limite
        if action in ['buy_stop', 'sell_stop', 'buy_stop_limit', 'sell_stop_limit']:
            price_trigger_match = re.search(r'(?i)preço ativação:\s*([\d.]+)', content)
            limit_price_match = re.search(r'(?i)preço limite:\s*([\d.]+)', content)

            if price_trigger_match:
                price_trigger = float(price_trigger_match.group(1))
                print(f"Preço de Ativação encontrado: {price_trigger}")  # Imprimir preço de ativação
            else:
                raise ValueError("Preço de ativação não encontrado para ordem Stop ou Stop Limit.")

            if limit_price_match:
                limit_price = float(limit_price_match.group(1))
                print(f"Preço Limite encontrado: {limit_price}")  # Imprimir preço limite
            else:
                raise ValueError("Preço limite não encontrado para ordem Stop Limit.")
        
        # Se a ação for Buy Limit ou Sell Limit, extrair o preço limite
        elif action in ['buy_limit', 'sell_limit']:
            limit_price_match = re.search(r'(?i)preço limite:\s*([\d.]+)', content)
            if limit_price_match:
                limit_price = float(limit_price_match.group(1))
                print(f"Preço Limite encontrado: {limit_price}")  # Imprimir preço limite
            else:
                raise ValueError("Preço limite não encontrado para ordem Limit.")

        # Retornar os valores relevantes
        return action, stop_loss_points, take_profit_points, price_trigger, limit_price

    except Exception as e:
        print(f"Erro ao analisar o sinal de trade: {e}")
        return None, None, None, None, None
