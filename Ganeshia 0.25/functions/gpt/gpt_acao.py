import openai
from typing import Tuple, Optional
import re
from functions.extract import extract_only_action, extract_certainty_percentage

def get_trade_signal_action(prompt: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """
    Função para obter a ação de trade (buy, sell, etc.) e a porcentagem de certeza.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um analista de mercado. Forneça respostas objetivas e concisas, sem explicações longas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        
        content = response.choices[0].message['content'].strip()
        print(f"Resposta completa do GPT: {content}")  # Exibe a resposta completa para debugging

        # Extrair apenas a ação
        action = extract_only_action(content)
        
        # Extrair porcentagem de certeza
        certainty = extract_certainty_percentage(content)

        if action and certainty is not None:
            return content, action, certainty
        else:
            print("Erro: Ação ou certeza não foram extraídas corretamente.")
            return None, None, None

    except Exception as e:
        print(f"Erro ao buscar a ação de trade: {e}")
        return None, None, None
