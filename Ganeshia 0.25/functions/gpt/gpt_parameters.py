import openai
from typing import Tuple, Optional, Dict
from functions.extract import extract_trade_parameters

def get_trade_signal_parameters(prompt, action_line):
    """
    Função para pegar os parâmetros: Stop Loss, Take Profit, Preço de Ativação (Price Trigger), e Preço Limite (Limit Price).
    """
    try:
        full_prompt = f"{prompt}"
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um analista de mercado. Forneça respostas objetivas e concisas, sem explicações longas."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=100
        )
        content = response.choices[0].message['content'].strip()
        print(content)
        
        # Extrair Stop Loss, Take Profit, Preço de Ativação e Preço Limite
        trade_params = extract_trade_parameters(content, action_line)

        return content, trade_params

    except Exception as e:
        print(f"Erro ao buscar parâmetros do trade: {e}")
        return None, {
            "order_type": None,
            "take_profit": None,
            "stop_loss": None,
            "limit_price": None,
            "trigger_price": None
        }