import MetaTrader5 as mt5
import pandas as pd
import json
from datetime import datetime, timedelta

# Função para obter o histórico de operações
def get_trade_history():
    # Define o intervalo de tempo (últimas 24 horas)
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)

    # Obtém o histórico de operações no intervalo de tempo especificado
    history_deals = mt5.history_deals_get(start_time, end_time)

    if history_deals is None:
        print(f"Erro ao obter o histórico de operações, erro: {mt5.last_error()}")
        return pd.DataFrame()  # Retorna DataFrame vazio em caso de erro

    if len(history_deals) == 0:
        print("Nenhuma operação encontrada no intervalo especificado.")
        return pd.DataFrame()  # Retorna um DataFrame vazio

    # Converte os dados em um DataFrame
    columns = history_deals[0]._asdict().keys()  # Obtém os nomes das colunas
    df = pd.DataFrame([deal._asdict() for deal in history_deals], columns=columns)
    df['time'] = pd.to_datetime(df['time'], unit='s')  # Converte o tempo
    df = df.drop(columns=['fee', 'ticket', 'time_msc', 'magic', 'comment', 'commission', 'swap', 'external_id'])  # Remove colunas desnecessárias
    df.set_index('time', inplace=True)  # Define o índice com base no tempo
    return df

# Função para atualizar o JSON
def atualizar_json_com_ultima_operacao(json_file, symbol):
    # Carrega o conteúdo do arquivo JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        operacoes_json = json.load(f)

    # Obtém o histórico de operações
    operacoes_mt5 = get_trade_history()

    if operacoes_mt5.empty:
        print("Nenhuma operação no histórico para atualizar.")
        return

    # Percorre cada operação no JSON e tenta encontrar correspondência no MT5
    for operacao in operacoes_json:
        if operacao["Símbolo"] == symbol and operacao["Preço de Fechamento"] is None:
            position_id = operacao.get("position_id")  # Supondo que o position_id esteja no JSON

            # Procura uma operação no MT5 com o mesmo símbolo e position_id
            operacao_mt5 = operacoes_mt5[operacoes_mt5['position_id'] == position_id]

            if not operacao_mt5.empty:
                # Pega a segunda operação correspondente, se existir
                if len(operacao_mt5) > 1:
                    segunda_operacao = operacao_mt5.iloc[1]  # A segunda operação

                    # Verifica se o lucro/prejuízo está correto
                    print(f"Lucro/Prejuízo encontrado no MT5: {segunda_operacao['profit']}")
                    
                    # Preenche os campos faltantes no JSON
                    operacao["Preço de Fechamento"] = segunda_operacao['price']
                    operacao["Lucro/Prejuízo"] = segunda_operacao['profit']
                    print(f"Operação atualizada: {operacao}")
                else:
                    print(f"Apenas uma operação encontrada para o position_id {position_id}.")

    # Salva o JSON atualizado
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(operacoes_json, f, ensure_ascii=False, indent=4)
    print("JSON atualizado com sucesso.")
