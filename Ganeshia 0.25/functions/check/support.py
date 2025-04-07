def check_support_resistance_levels(price, supports, resistances, support_threshold=0.01, resistance_threshold=0.01):
    for level in supports:
        if abs(price - level) / level < support_threshold:
            return "Próximo ao suporte", level
    
    for level in resistances:
        if abs(price - level) / level < resistance_threshold:
            return "Próximo à resistência", level
    
    return "Nenhum nível próximo", None
