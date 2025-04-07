from typing import Tuple, Optional
import re

def extract_certainty_percentage(content: str) -> Optional[int]:
    """
    Extrai a porcentagem de certeza (número seguido de '%') do texto da resposta.
    """
    try:
        # Captura o número seguido de "%" e converte para int
        certainty_match = re.search(r'(\d+)%', content)
        if certainty_match:
            certainty = int(certainty_match.group(1))
            print(f"Certeza encontrada: {certainty}%")
            return certainty
        else:
            print("Certeza não encontrada.")
            return None
    except Exception as e:
        print(f"Erro ao analisar a certeza: {e}")
        return None
