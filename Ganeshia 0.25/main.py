from datetime import datetime, timedelta
import MetaTrader5 as mt5 
import requests
import openai  
import os
import time

# Importação das funções
from functions.get import get_data
from functions.prompts import gerar_prompt_acao, selecionar_estrategia, gerar_prompt_parametros, gerar_prompt_gpt, get_last_trade_info
from functions.calculate import calculate_indicators, calculate_moving_averages
from functions.place import place_order, place_limit_order, place_stop_order, place_stop_limit_order
from functions.gpt import get_trade_signal_action, get_close_or_reassess_signal, get_trade_signal_parameters
from functions.extra import news, check_market_conditions, has_open_trade, analyze_trend_and_support
from functions.check import verify_conditions
from data_base import verificar_operacoes_passadas, atualizar_operacao_com_dados_json, carregar_dados_mt5_para_banco, criar_tabela_operacoes, verificar_operacoes_passadas


# Configuração dos detalhes da conta
ACCOUNTS = [
    {"account": 515969287, "password": '8rD4Fie@', "server": 'XPMT5-DEMO', "nome": 'Felipe', "lucros": 0}
]

# Configuração da chave da API da OpenAI
OPENAI_API_KEY = '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'

# Função para conectar ao MetaTrader 5
def connect_to_mt5(account_info):
    if not mt5.initialize():
        print("Falha ao inicializar o MetaTrader 5, erro:", mt5.last_error())
        return False
    
    authorized = mt5.login(account_info['account'], password=account_info['password'], server=account_info['server'])
    if not authorized:
        print(f"Login falhou para a conta {account_info['nome']}, código do erro =", mt5.last_error())
        mt5.shutdown()
        return False

    return True

# Conectar ao ChatGPT
openai.api_key = OPENAI_API_KEY

def solicitar_volume():
    while True:
        try:
            volume = int(input(f"Quantos contratos deseja operar hoje?  "))
            valor_operacao = volume * 0.20
            print(f"\nVocê escolheu {volume} contratos, com valor total de {valor_operacao:.2f}\n")
            
            confirmacao = input("Confirma a operação? (sim/não): \n").lower()
            
            if confirmacao == 'sim':
                return volume
            else:
                print("Operação não confirmada, por favor insira novamente o volume.")
        
        except ValueError:
            print("Por favor, insira um número válido.")

def guardar_op(acao, lucro, preju, filename='operacao.txt'):
    # Formata a string da operação com 3 linhas
    operacao_info = (
        f"Operação atual é de: {acao}\n"
        f"Com Take Profit de: {lucro}\n"
        f"Com Stop Loss de: {preju}\n"
    )
    
    # Cria ou sobrescreve o arquivo txt com as informações
    with open(filename, 'w') as file:
        # Limita a escrita a 3 linhas
        file.write(operacao_info.strip())  # Usa strip() para garantir que não há linhas em branco extras

    return filename  # Retorna o nome do arquivo para ser usado depois

import json

def ler_arquivo_operacao(filepath=r'C:\Users\User\Trabalho\Ganeshia 0.25\operacoes.json'):
    try:
        with open(filepath, encoding='utf-8') as file:
            data = json.load(file)
            
            # Verifica se o JSON é uma lista e acessa o primeiro elemento
            if isinstance(data, list) and data:
                data = data[0]  # Pega o primeiro item da lista (a operação atual)
            
            # Verifica se "Tipo de Operação" existe no dicionário
            tipo_operacao = data.get("Tipo de Operação", "").lower()
            
            # Mapeia tipos de operação para termos mais descritivos e atualiza o campo no dicionário
            if tipo_operacao in ["buy", "buy_stop", "buy_limit"]:
                data["Tipo de Operação"] = "compra"
            elif tipo_operacao in ["sell", "sell_stop", "sell_limit"]:
                data["Tipo de Operação"] = "venda"
            else:
                raise ValueError("Tipo de operação desconhecido no arquivo JSON.")
            
            return data  # Retorna o dicionário completo com o tipo de operação atualizado
    
    except json.JSONDecodeError:
        print("Erro: Falha ao decodificar o arquivo JSON. Verifique a formatação.")
    except FileNotFoundError:
        print("Erro: Arquivo JSON não encontrado.")
    except ValueError as e:
        print(f"Erro: {e}")
    
    return None


def obter_lucro_24h():
    agora = datetime.now()
    
    # Define o início como hoje às 9:00
    hoje = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Se agora for antes das 9:00, ajuste para pegar o histórico de ontem às 9:00
    if agora < hoje:
        hoje -= timedelta(days=1)

    # Obter histórico de operações fechadas desde hoje às 9:00
    historico = mt5.history_deals_get(hoje, agora)
    
    if historico is None:
        print("Nenhum histórico de transações encontrado, erro:", mt5.last_error())
        return 0
    
    # Inicializa as variáveis para lucros e prejuízos
    lucro_total = 0.0
    prejuizo_total = 0.0
    
    # Calcular o lucro total, somando todos os profits
    for deal in historico:
        if deal.profit is not None:
            if deal.profit > 0:
                lucro_total += deal.profit
            elif deal.profit < 0:
                prejuizo_total += abs(deal.profit)  # Armazena o valor absoluto do preju

    # Calcular o resultado total
    resultado_total = lucro_total - prejuizo_total
    
    return resultado_total

def get_current_price(symbol):
    # Inicializa o MetaTrader 5
    if not mt5.initialize():
        print(f"Erro ao inicializar o MetaTrader 5: {mt5.last_error()}")
        return None

    # Obtém as informações do tick do símbolo
    tick = mt5.symbol_info_tick(symbol)
    
    if tick is None:
        print(f"Erro ao obter informações do símbolo {symbol}: {mt5.last_error()}")
        return None

    # Retorna o preço de venda atual (bid) como um float
    return float(tick.bid)

def main():
    symbol = 'WINZ24'
    interval = mt5.TIMEFRAME_M5
    num_candles = 288

    global total_profit
    global attempt_count

    # Preparar dados históricos e dividir em treino/teste para Machine Learning
    data = get_data(symbol, interval, num_candles)
    
    criar_tabela_operacoes()

    account_info = ACCOUNTS[0]  # Pega a primeira conta, pode ser adaptado para múltiplas contas
    usuario = {account_info['nome']}
    
    print(f"\n----------------------------------------------------------------------------------------\n\n"
          f"Bem-vindo, {account_info['nome']}"
          f"\n\n----------------------------------------------------------------------------------------\n")
    
    volume = solicitar_volume()
    print(f"\nVolume confirmado: {volume} contratos.\n")

    META_LUCRO = (volume * 0.20) * 5000  # Meta de lucro em reais
    META_PREJUÍZO = (volume * 0.20) * -2000  # Meta de prejuízo em reais
    total_profit = obter_lucro_24h()

    print(f"Meta de lucro: R${META_LUCRO:.2f}")

    while True:
        for account_info in ACCOUNTS:
            if not connect_to_mt5(account_info):
                continue

        if not mt5.symbol_select(symbol, True):
            print(f"Falha ao selecionar o símbolo {symbol}, tentando novamente em 60 segundos...")
            time.sleep(60)
            continue
        
        # Verificar se a meta de lucro ou limite de prejuízo já foi atingido
        if total_profit >= META_LUCRO or total_profit <= META_PREJUÍZO:
            if total_profit >= META_LUCRO:
                print(f"Meta de lucro atingida: {META_LUCRO:.2f}. Encerrando operações.")
            elif total_profit <= META_PREJUÍZO:
                print(f"Meta de prejuízo atingida: {META_PREJUÍZO:.2f}. Encerrando operações.")
            break

        print(f"Lucros do dia: {total_profit}\nMeta de hoje: {META_LUCRO}")

        # Carregar e atualizar dados
        carregar_dados_mt5_para_banco()
        atualizar_operacao_com_dados_json()

        # Obter e processar os dados de mercado
        data = get_data(symbol, interval, num_candles)
        if data is None or data.empty:
            print("Nenhum dado recuperado, tentando novamente em 60 segundos...")
            time.sleep(60)
            continue

        # Calcular indicadores e tendências
        data = calculate_indicators(data)
        last_price = data['close'].iloc[-1]
        ma_data = calculate_moving_averages(data)
        trend_info = analyze_trend_and_support(data)

        # Parte 1: Verificar se há operação aberta e checar as condições para fechar ou manter
        if has_open_trade(symbol):
            print("Operação em andamento\n----------------------------------------------------------------------------------------")
            attempt_count = 1  # Inicializa o contador de tentativas

            # Obtém o tipo da operação atual (compra/venda) do arquivo ou de outra fonte
                        # Obtém o tipo da operação atual do arquivo
            op_atual = ler_arquivo_operacao()

            # Verifique se `op_atual` é válido antes de passar para `verify_conditions`
            if op_atual and isinstance(op_atual, dict):
                conditions, is_ready, messages = verify_conditions(data, last_price, trend_info['supports'], trend_info['resistances'], op_atual)
            else:
                print("Erro: A operação atual não está disponível ou não está no formato esperado.")

            while attempt_count <= 6:
                # Obter dados e verificar as condições
                data = get_data(symbol, interval, num_candles)
                last_price = data['close'].iloc[-1]
                trend_info = analyze_trend_and_support(data)

                # Chama a função verify_conditions para checar todas as condições e obter o dicionário e status de prontidão
                conditions, is_ready, message = verify_conditions(data, last_price, trend_info['supports'], trend_info['resistances'], op_atual)

                if is_ready:
                    print("Cinco ou mais condições opostas à operação atual foram atendidas. Prosseguindo para decisão GPT.")
                    last_trade_info = get_last_trade_info(symbol)
                    prompt = gerar_prompt_gpt(last_trade_info, conditions, message)

                    # Consulta a função de decisão GPT e processa a resposta
                    response_explanation, action_line = get_close_or_reassess_signal(prompt, symbol)
                    print(response_explanation)
                    break  # Sai do loop se houver decisão
                else:
                    print(f"Condições insuficientes ou direções não contrárias. Tentativa {attempt_count} de 6.")
                    attempt_count += 1

                time.sleep(300)  # Espera 5 minutos antes da próxima verificação

                # Checa novamente se a operação ainda está aberta
                if not has_open_trade(symbol):
                    print("Nenhuma operação em andamento. Saindo do loop.")
                    break  # Sai do loop se não houver operação

            # Se não houve uma decisão após 30 minutos
            if attempt_count >= 6:
                print("30 minutos sem resposta. Decisão final via GPT.")
                # Atualiza dados para a verificação final
                data = get_data(symbol, interval, num_candles)
                last_price = data['close'].iloc[-1]
                trend_info = analyze_trend_and_support(data)

                # Chama novamente verify_conditions antes de gerar a decisão GPT
                conditions, is_ready, message = verify_conditions(data, last_price, trend_info['supports'], trend_info['resistances'], op_atual)
                
                last_trade_info = get_last_trade_info(symbol)
                prompt = gerar_prompt_gpt(last_trade_info, conditions, message)

                # Executa a função de decisão final via GPT
                response_explanation, action_line = get_close_or_reassess_signal(prompt, symbol)
                print(response_explanation)


        # Parte 2: Verificar condições para abrir novas operações
        else:
            print("Nenhuma operação em andamento. Verificando se há oportunidades para abrir nova operação.")

            message, ready, condicoes, details_message = check_market_conditions(data)
            print(f"Análise de Condição de Mercado: {message}")

            # Verifica o status 'ready' e age de acordo1
            if not ready:
                print(f"Gráfico não apto para operação. {details_message}")
                print("----------------------------------------------------------------------------------------")
                time.sleep(300)
                continue
            else:
                print("Gráfico apto para operação com as seguintes condições de mercado:")
                print(details_message)

            # Verificar operações passadas similares
            operacoes_passadas = verificar_operacoes_passadas(condicoes)
            if operacoes_passadas:
                print(f"Operações passadas encontradas: {operacoes_passadas}")
            else:
                print("Nenhuma operação passada encontrada com as mesmas condições.")
                
      
            data_atual = datetime.now().strftime('%d%m%Y')
            url = f'https://www.infomoney.com.br/mercados/mini-indice-hoje-futuro-ibovespa-winz24-{data_atual}/'
            response = requests.get(url)

            noticia = news(response)
            
            current_price = get_current_price(symbol)

            prompt_acao = gerar_prompt_acao(symbol, data, ma_data, trend_info, condicoes, message,  noticia, operacoes_passadas, current_price, total_profit, META_LUCRO, META_PREJUÍZO)
            
            # Obter ação do GPT
            response_content, action_line, certeza = get_trade_signal_action(prompt_acao)

            if action_line and certeza is not None:
                print(f"Ação recomendada: {action_line}")
                estrategia = selecionar_estrategia(action_line)
                prompt_parametros = gerar_prompt_parametros(symbol, data, ma_data, trend_info, condicoes, message, current_price, action_line, estrategia, certeza, total_profit, META_LUCRO, META_PREJUÍZO)
                response_content, trade_params = get_trade_signal_parameters(prompt_parametros, action_line)    

                # Extração dos parâmetros
                stop_loss = trade_params.get('stop_loss')
                take_profit = trade_params.get('take_profit')
                price_trigger = trade_params.get('trigger_price')
                limit_price = trade_params.get('limit_price')

                if stop_loss is None or take_profit is None:
                    print("Erro ao obter os parâmetros do trade.")
                    continue

                # Abrir a operação com base na ação
                if action_line in ['buy', 'sell']:
                    place_order(ACCOUNTS[0], symbol, action_line, stop_loss, take_profit, response_content, condicoes, usuario, volume)
                elif action_line in ['buy_limit', 'sell_limit'] and limit_price is not None:
                    place_limit_order(ACCOUNTS[0], symbol, action_line, limit_price, stop_loss, take_profit, response_content, condicoes, usuario, volume)
                elif action_line in ['buy_stop', 'sell_stop'] and price_trigger is not None:
                    place_stop_order(ACCOUNTS[0], symbol, action_line, price_trigger, stop_loss, take_profit, response_content, condicoes, usuario, volume)
                elif action_line in ['buy_stop_limit', 'sell_stop_limit'] and price_trigger is not None and limit_price is not None:
                    place_stop_limit_order(ACCOUNTS[0], symbol, action_line, price_trigger, limit_price, stop_loss, take_profit, response_content, condicoes, usuario, volume)
                
            else:
                print("Erro ao obter a ação recomendada.")
                time.sleep(300)

        mt5.shutdown()
        time.sleep(300)

if __name__ == "__main__":
    main()
