def gerar_prompt_parametros(symbol, data, ma_data, trend_info, condicoes, message, current_price, action_line, estrategia, certeza, total_profit, META_LUCRO, META_PREJUÍZO):
    # Conversão dos valores para pontos
    total_profit_pontos = total_profit * 5
    meta_lucro_pontos = META_LUCRO * 5
    meta_prejuizo_pontos = abs(META_PREJUÍZO) * 5

    # Cálculo de pontos restantes para metas
    pontos_restantes_lucro = max(meta_lucro_pontos - total_profit_pontos, 0)
    pontos_restantes_prejuizo = max(total_profit_pontos - meta_prejuizo_pontos, 0)

    # Definição dos valores de Take Profit (TP) e Stop Loss (SL) com base na certeza da ação
    tp_valor = min(int(500 * (certeza / 100)), 500)  # Máximo de 500 pontos
    sl_valor = min(int(200 * (certeza / 100)), 200)  # Máximo de 200 pontos

    prompt_parametros = (
        f"**INSTRUÇÕES DE DAY TRADING**\n"
        f"\n**ANÁLISE DO ATIVO {symbol}**:\n"
        f"- Sugestão do Bot:\n"
        f"- {message}"
        f"- Últimos candles analisados: {data.tail(50)}\n"
        f"- Condições de mercado atendidas: {condicoes}\n"
        f"- Médias Móveis:\n"
        f"  - MA 7 períodos: {ma_data['MA_7'].iloc[-1]}\n"
        f"  - MA 22 períodos: {ma_data['MA_22'].iloc[-1]}\n"
        f"  - MA 50 períodos: {ma_data['MA_50'].iloc[-1]}\n"
        f"- Tendências:\n"
        f"  - Primária: {trend_info['primary_trend']}\n"
        f"  - Secundária: {trend_info['secondary_trend']}\n"
        f"- Níveis de Suporte e Resistência:\n"
        f"  - Suporte: {trend_info['supports']}\n"
        f"  - Resistência: {trend_info['resistances']}\n"
        f"- Preço atual: {current_price}\n"
        f"\n**STATUS DA META DIÁRIA EM PONTOS**:\n"
        f"- Lucro acumulado: {total_profit_pontos:.0f} pontos\n"
        f"- Meta de lucro diária: {meta_lucro_pontos:.0f} pontos\n"
        f"- Limite de prejuízo diário: {meta_prejuizo_pontos:.0f} pontos\n"
        f"- Pontos restantes para atingir a meta de lucro: {pontos_restantes_lucro:.0f} pontos\n"
        f"- Pontos restantes antes do limite de prejuízo: {pontos_restantes_prejuizo:.0f} pontos\n"
        f"\n**PARÂMETROS RECOMENDADOS PARA ORDENS**:\n"
        f"- Take Profit (TP): {tp_valor} pontos (máximo: {pontos_restantes_lucro:.0f} pontos)\n"
        f"- Stop Loss (SL): {sl_valor} pontos (máximo: 200 pontos)\n"
        f"- Ajuste TP e SL entre 0,5% e 2% acima ou abaixo do preço atual.\n"
        f"\n**AÇÃO SELECIONADA**: {action_line}\n"
        f"\n**ESTRATÉGIA SUGERIDA**:\n{estrategia}\n"
        f"\n**FORMATO DE RESPOSTA PARA PARÂMETROS**:\n"
        f"- Informe apenas o nome do parâmetro e o valor, múltiplos de 5.\n"
        f"\n**EXEMPLO DE FORMATAÇÃO**:\n"
        f"Stop Loss: valor (exemplo: 300, comparado ao Preço Limite ou Preço de Ativação)\n"
        f"Take Profit: valor (exemplo: 100, comparado ao Preço Limite ou Preço de Ativação)\n"
        f"Preço Limite: valor (exemplo: 130000)\n"
        f"Preço de Ativação: valor (exemplo: 130000)\n"
    )
    return prompt_parametros
