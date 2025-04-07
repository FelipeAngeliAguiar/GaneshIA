import json
import os
from datetime import datetime
from collections import OrderedDict
import MetaTrader5 as mt5
from data_base import inserir_operacao_no_banco

# Caminho do arquivo JSON que armazenará as operações
JSON_FILE_PATH = r'C:\Users\User\Trabalho\Ganeshia 0.25\operacoes.json'

def criar_arquivo_json():
    """
    Cria o arquivo JSON se ele não existir.
    """
    if not os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'w') as f:
            json.dump([], f)
        print(f"Arquivo JSON criado em: {JSON_FILE_PATH}")

def registrar_abertura_operacao(justificativa, id_position, condicoes_mercado, usuario, action):
    """
    Registra a abertura de uma operação salvando no JSON apenas os campos necessários:
    usuário, id_position, justificativa e condições de mercado.
    """
    # Verifique se condicoes_mercado é um dicionário ou lista
    if isinstance(condicoes_mercado, set):
        condicoes_mercado = list(condicoes_mercado)
    elif not isinstance(condicoes_mercado, (dict, list)):
        print(f"Erro: 'condicoes_mercado' deve ser um dicionário ou lista, recebido {type(condicoes_mercado).__name__}")
        return

    # Cria o arquivo JSON se ele não existir
    criar_arquivo_json()

    # Nova operação a ser registrada (usando OrderedDict para garantir a ordem dos campos)
    operacao = OrderedDict([
        ('Usuário', usuario),               # Adicionando o nome do usuário à operação
        ('id_position', id_position),       # ID da posição no MT5
        ('Justificativa', justificativa),   # Justificativa da operação
        ('Condições', condicoes_mercado),   # Condições de mercado
        ('Tipo de Operação', action)
    ])

    # Ler o conteúdo atual do arquivo JSON
    with open(JSON_FILE_PATH, 'r') as f:
        operacoes = json.load(f)

    # Adicionar a nova operação
    operacoes.append(operacao)

    # Salvar no arquivo JSON
    with open(JSON_FILE_PATH, 'w') as f:
        json.dump(operacoes, f, indent=4)

    print(f"Operação aberta registrada: {operacao}")

    # Insere a operação no banco de dados (função separada)
    inserir_operacao_no_banco(operacao)

