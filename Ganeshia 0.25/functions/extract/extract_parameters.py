import re
from typing import Dict, Optional

def extract_trade_parameters(content: str, order_type: str) -> Dict[str, Optional[int]]:
    """
    Extrai Stop Loss, Take Profit, Preço de Ativação (Trigger Price) e Preço Limite (Limit Price) do conteúdo.
    Retorna valores dependendo do tipo de ordem (Buy/Sell Stop, Buy/Sell Limit, ou Stop Limit).
    Todos os valores numéricos são arredondados e convertidos para inteiros para evitar valores com decimais.
    """
    try:
        # Extrair Stop Loss e Take Profit usando expressões regulares
        sl_match = re.search(r'(?i)stop loss:\s*([\d.,]+)', content)
        tp_match = re.search(r'(?i)take profit:\s*([\d.,]+)', content)

        if not sl_match or not tp_match:
            raise ValueError("Stop Loss ou Take Profit não encontrado no conteúdo.")

        # Arredondar e converter para inteiros para evitar casas decimais
        stop_loss_points = int(round(float(sl_match.group(1).replace(",", "."))))
        take_profit_points = int(round(float(tp_match.group(1).replace(",", "."))))

        # Inicializar variáveis para Preço de Ativação (Trigger Price) e Preço Limite (Limit Price)
        price_trigger = None
        limit_price = None

        # Verificar se a ordem é Limit (Buy Limit ou Sell Limit)
        if order_type.lower() in ['buy_limit', 'sell_limit']:
            limit_price_match = re.search(r'(?i)preço limite:\s*([\d.,]+)', content)
            if limit_price_match:
                limit_price = int(round(float(limit_price_match.group(1).replace(",", "."))))
            return {
                "order_type": order_type,
                "take_profit": take_profit_points,
                "stop_loss": stop_loss_points,
                "limit_price": limit_price,
                "trigger_price": None
            }

        # Verificar se a ordem é Stop (Buy Stop ou Sell Stop)
        elif order_type.lower() in ['buy_stop', 'sell_stop']:
            price_trigger_match = re.search(r'(?i)preço\s*(de\s*)?ativ[aã]ção:\s*([\d.,]+)', content)
            if price_trigger_match:
                price_trigger = int(round(float(price_trigger_match.group(2).replace(",", "."))))
            else:
                print("Aviso: Preço de ativação não encontrado no conteúdo. Definindo como 0.")
                price_trigger = 0  # Definir um valor padrão

            return {
                "order_type": order_type,
                "take_profit": take_profit_points,
                "stop_loss": stop_loss_points,
                "limit_price": None,
                "trigger_price": price_trigger
            }

        # Verificar se a ordem é Stop Limit (Buy Stop Limit ou Sell Stop Limit)
        elif order_type.lower() in ['buy_stop_limit', 'sell_stop_limit']:
            # Para stop_limit, precisamos de Preço de Ativação e Preço Limite
            price_trigger_match = re.search(r'(?i)preço\s*(de\s*)?ativ[aã]ção:\s*([\d.,]+)', content)
            limit_price_match = re.search(r'(?i)preço limite:\s*([\d.,]+)', content)

            if price_trigger_match:
                price_trigger = int(round(float(price_trigger_match.group(2).replace(",", "."))))
            else:
                raise ValueError("Preço de ativação não encontrado para ordem stop_limit.")
            
            if limit_price_match:
                limit_price = int(round(float(limit_price_match.group(1).replace(",", "."))))
            else:
                raise ValueError("Preço limite não encontrado para ordem stop_limit.")

            return {
                "order_type": order_type,
                "take_profit": take_profit_points,
                "stop_loss": stop_loss_points,
                "limit_price": limit_price,
                "trigger_price": price_trigger
            }

        # Verificar se a ordem é uma ordem direta de compra ou venda (Buy ou Sell)
        elif order_type.lower() in ['buy', 'sell']:
            # Ordens de Buy e Sell só precisam de SL e TP
            return {
                "order_type": order_type,
                "take_profit": take_profit_points,
                "stop_loss": stop_loss_points,
                "limit_price": None,
                "trigger_price": None
            }

        else:
            raise ValueError("Tipo de ordem não reconhecido. Deve ser 'buy_limit', 'sell_limit', 'buy_stop', 'sell_stop', 'buy_stop_limit', 'sell_stop_limit', 'buy', ou 'sell'.")

    except Exception as e:
        print(f"Erro ao analisar os parâmetros do trade: {e}")
        return {
            "order_type": order_type,
            "take_profit": None,
            "stop_loss": None,
            "limit_price": None,
            "trigger_price": None
        }
