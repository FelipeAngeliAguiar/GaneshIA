import re

def extract_close_or_reassess_action(content):
    """
    Função para extrair a decisão (fechar ou manter) da resposta do GPT,
    permitindo maior flexibilidade na identificação.
    """
    try:
        # Busca por "fechar" ou "manter" em qualquer contexto da resposta
        action_match = re.search(r'\b(fechar|manter)\b', content, re.IGNORECASE)
        
        # Se "fechar" ou "manter" estiver presente, extrai a ação correspondente
        action = action_match.group(1).lower() if action_match else "manter"
        
        # Formata a linha da ação para consistência
        action_line = f"Ação: {action.capitalize()}"
        
        return action_line
    except Exception as e:
        print(f"Error parsing close/reassess signal: {e}")
        return "Error in GPT response analysis", None
