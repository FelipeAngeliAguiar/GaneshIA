import re
from typing import Optional

def extract_only_action(content: str) -> Optional[str]:
    try:
        # Captura a ação diretamente
        action_match = re.search(r'\b(buy|sell|buy_stop|sell_stop|buy_limit|sell_limit|buy_stop_limit|sell_stop_limit)\b', content, re.IGNORECASE)
        if action_match:
            action = action_match.group(1).lower()
            print(f"Ação encontrada: {action}")
            return action
        else:
            print("Ação não encontrada.")
            return None
    except Exception as e:
        print(f"Erro ao analisar a ação: {e}")
        return None
