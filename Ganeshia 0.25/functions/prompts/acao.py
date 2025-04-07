def gerar_prompt_acao(symbol, data, ma_data, trend_info, condicoes, message, noticia, operacoes_passadas, current_price, total_profit, META_LUCRO, META_PREJUÍZO):
    # Conversão de valores para pontos
    total_profit_pontos = total_profit * 5
    meta_lucro_pontos = META_LUCRO * 5
    meta_prejuizo_pontos = abs(META_PREJUÍZO) * 5

    # Cálculo de pontos restantes para metas
    pontos_restantes_lucro = max(meta_lucro_pontos - total_profit_pontos, 0)
    pontos_restantes_prejuizo = max(total_profit_pontos - meta_prejuizo_pontos, 0)

    # Análise das operações passadas
    ajuste_estrategia = ""
    if operacoes_passadas:
        ultima_operacao = operacoes_passadas[-1]  # Última operação
        lucro_prejuizo_anterior = ultima_operacao.get('lucro_prejuizo', 0)
        tipo_operacao = "comprar" if lucro_prejuizo_anterior >= 0 else "vender"
        
        ajuste_estrategia = (
            f"- **Ajuste de Estratégia**: A última operação foi {'lucrativa' if lucro_prejuizo_anterior >= 0 else 'não lucrativa'} com {abs(lucro_prejuizo_anterior)} pontos.\n"
            f"  - Sugestão: Considere {'manter a estratégia de ' + tipo_operacao if lucro_prejuizo_anterior >= 0 else 'ajustar para ' + ('comprar' if lucro_prejuizo_anterior < 0 else 'vender') + ' se as condições permitirem'}.\n"
            f"  - Detalhes da operação anterior: {ultima_operacao.get('justificativa')}\n"
        )
    else:
        ajuste_estrategia = "- **Nota**: Não há operações passadas para avaliar ajustes.\n"

    # Criação do prompt com ajustes
    prompt_acao = (
        f"**INSTRUÇÕES DE TRADING**\n"
        f"{ajuste_estrategia}\n"
        f"- **Avaliação do Momento**: Se você não tem certeza se este é o momento adequado para abrir uma operação, é melhor não agir. Espere por melhores oportunidades que ofereçam maior segurança.\n"
        f"- Evite abrir novas operações em momentos de alta volatilidade.\n"
        f"- Analise a correlação entre ativos antes de decidir novas posições.\n"
        f"- Ultima noticia do ativo:\n"
        f"- {noticia}\n"
        f"\n**ANÁLISE DO ATIVO {symbol}**:\n"
        f"- Dados recentes: {data.tail(50)}\n"
        f"- **SUGESTÃO DO BOT**: \n"
        f" - {message}\n"
        f"- Condições do mercado atendidas:\n {condicoes}\n"
        f"- Médias Móveis:\n"
        f"  - MA 7: {ma_data['MA_7'].iloc[-1]}\n"
        f"  - MA 22: {ma_data['MA_22'].iloc[-1]}\n"
        f"  - MA 50: {ma_data['MA_50'].iloc[-1]}\n"
        f"- Tendências:\n"
        f"  - Primária: {trend_info['primary_trend']}\n"
        f"  - Secundária: {trend_info['secondary_trend']}\n"
        f"- Suportes: {trend_info['supports']}\n"
        f"- Resistências: {trend_info['resistances']}\n"
        f"- Preço atual: {current_price}\n"
        f"\n**STATUS DA META DIÁRIA EM PONTOS**\n"
        f"- Lucro acumulado: {total_profit_pontos:.0f} pontos\n"
        f"- Meta de lucro: {meta_lucro_pontos:.0f} pontos\n"
        f"- Limite de prejuízo: {meta_prejuizo_pontos} pontos\n"
        f"- Faltam {pontos_restantes_lucro:.0f} pontos para a meta de lucro.\n"
        f"- Faltam {pontos_restantes_prejuizo:.0f} pontos antes de atingir o limite de prejuízo.\n"
        f"\n**DECISÃO DE OPERAÇÃO**:\n"
        f"- **Critérios de Ação**:\n"
        f"  - Priorize 'buy' se a tendência for de alta ou houver reversão de baixa para alta.\n"
        f"  - Priorize 'sell' se a tendência for de baixa ou houver reversão de alta para baixa.\n"
        f"  - Mantenha a posição se a certeza for menor que 90%.\n"
        f"\n**TIPOS DE ORDENS DISPONÍVEIS**:\n"
        f"1. `buy` - Ordem de compra a mercado\n"
        f"2. `sell` - Ordem de venda a mercado\n"
        f"3. `buy_limit` - Ordem de compra com limite\n"
        f"   - Use se você espera que o preço suba até um ponto específico e depois caia. Exemplo: coloque um buy limit em x para comprar a um preço melhor.\n"
        f"4. `sell_limit` - Ordem de venda com limite\n"
        f"   - Use se você acha que o preço vai subir até um ponto x e depois cair. Coloque um sell limit em x para vender a um preço melhor.\n"
        f"5. `buy_stop` - Ordem de compra stop\n"
        f"   - Use se o preço atual estiver em tendência de alta e você quiser comprar apenas se o preço ultrapassar um determinado nível. Exemplo: se você acredita que uma quebra acima de x confirmará a alta.\n"
        f"6. `sell_stop` - Ordem de venda stop\n"
        f"   - Use se o preço atual estiver em tendência de baixa e você quiser vender apenas se o preço cair abaixo de um determinado nível. Exemplo: se você acredita que uma quebra abaixo de x confirmará a baixa.\n"
        f"\n**FORMATO DE RESPOSTA**:\n"
        f"Ação: 'manter', 'buy', 'sell', 'buy_limit', 'sell_limit', 'buy_stop', 'sell_stop'\n"
        f"Certeza: número% (Exemplo: 75%)"
    )
    return prompt_acao
