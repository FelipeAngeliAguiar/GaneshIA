import mysql.connector
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import json
import os

# Configurações do banco MySQL
DB_CONFIG = {
    'host': '26.137.96.26',
    'user': 'felps',      # Usuário do MySQL
    'password': '1303',   # Senha do MySQL
    'database': 'fear'    # Nome do banco criado
}

# Caminho do arquivo JSON
JSON_FILE_PATH = r'C:\Users\User\Trabalho\Ganeshia 0.25\operacoes.json'

# Função para conectar ao banco de dados
def connect_to_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None

# Função para criar a tabela de operações
def criar_tabela_operacoes():
    conn = connect_to_db()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS operacoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data_horario DATETIME,
            simbolo VARCHAR(10),
            tipo_operacao VARCHAR(20),
            preco_abertura FLOAT,
            preco_fechamento FLOAT,
            lucro_prejuizo FLOAT,
            justificativa TEXT,
            usuario VARCHAR(50),
            id_position INT UNIQUE,
            tendencia VARCHAR(20),
            macd VARCHAR(20),
            bollinger_bands VARCHAR(20),
            volume VARCHAR(20),
            padroes_candlestick TEXT,
            ema_9 VARCHAR(20)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Função para carregar o JSON
def carregar_dados_json():
    if not os.path.exists(JSON_FILE_PATH):
        print(f"O arquivo {JSON_FILE_PATH} não existe.")
        return None
    
    with open(JSON_FILE_PATH, 'r') as f:
        operacoes = json.load(f)
    
    return operacoes

# Função para buscar dados no JSON por id_position
def buscar_dados_no_json_por_id(operacoes_json, id_position):
    for operacao in operacoes_json:
        if operacao['id_position'] == id_position:
            return operacao
    return None

# Função para inserir uma operação no banco de dados
# Função para inserir uma operação no banco de dados
def inserir_operacao_no_banco(operacao):
    conn = connect_to_db()
    if conn is None:
        return
    
    cursor = conn.cursor()

    # Verifica se a operação já existe
    cursor.execute("SELECT COUNT(*) FROM operacoes WHERE id_position = %s", (operacao['id_position'],))
    if cursor.fetchone()[0] > 0:
        cursor.close()
        conn.close()
        return
    
    # Trunca o valor de 'bollinger_bands' se for maior que 20 caracteres
    bollinger_bands = operacao.get('bollinger_bands', 'N/A')[:20]
    
    sql = """
        INSERT INTO operacoes (
            data_horario, simbolo, tipo_operacao, preco_abertura, 
            preco_fechamento, lucro_prejuizo, justificativa, usuario, id_position, 
            tendencia, macd, bollinger_bands, volume, padroes_candlestick, ema_9
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    valores = (
        operacao['data_horario'], 
        operacao['simbolo'], 
        operacao['tipo_operacao'],
        operacao['preco_abertura'], 
        operacao['preco_fechamento'],  
        operacao['lucro_prejuizo'],  
        operacao.get('justificativa', None),
        operacao.get('usuario', None),
        operacao['id_position'], 
        operacao.get('tendencia', 'N/A'),
        operacao.get('macd', 'N/A'),
        bollinger_bands,  # Valor truncado para o limite da coluna
        operacao.get('volume', 'N/A'),
        operacao.get('padroes_candlestick', 'Não atendida'),
        operacao.get('ema_9', 'N/A')
    )

    cursor.execute(sql, valores)
    conn.commit()
    print(f"Operação '{operacao['simbolo']}' inserida no banco de dados.")
    cursor.close()
    conn.close()

# Função para mapear o tipo de operação
def mapear_tipo_operacao(deal, operacoes_json):
    json_operacao = buscar_dados_no_json_por_id(operacoes_json, deal.position_id)
    if json_operacao:
        return json_operacao.get('Tipo de Operação', 'desconhecido')  # Aqui buscamos o tipo de operação no JSON
    return 'desconhecido'

# Função para atualizar operações com dados ausentes a partir do JSON
def atualizar_operacao_com_dados_json():
    conn = connect_to_db()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        return
    
    try:
        cursor = conn.cursor(dictionary=True)

        # Selecionar operações com campos ausentes
        cursor.execute("""
            SELECT * FROM operacoes
            WHERE tendencia = 'N/A' OR macd = 'N/A' OR bollinger_bands = 'N/A'
            OR volume = 'N/A' OR padroes_candlestick = '' OR ema_9 = 'N/A'
        """)
        
        operacoes_incompletas = cursor.fetchall()

        if not operacoes_incompletas:
            print("Nenhuma operação incompleta encontrada.")
            cursor.close()
            conn.close()
            return

        print(f"{len(operacoes_incompletas)} operações incompletas encontradas. Tentando completar...")

        # Carregar o JSON
        operacoes_json = carregar_dados_json()
        if operacoes_json is None:
            print("Erro ao carregar o arquivo JSON.")
            cursor.close()
            conn.close()
            return

        # Atualizar operações no banco com os dados do JSON
        for operacao in operacoes_incompletas:
            # Revalidar a conexão antes de cada operação
            if not conn.is_connected():
                print("Reconectando ao banco de dados...")
                conn = connect_to_db()
                if conn is None:
                    print("Falha ao reconectar ao banco de dados.")
                    break
                cursor = conn.cursor(dictionary=True)

            json_operacao = buscar_dados_no_json_por_id(operacoes_json, operacao['id_position'])

            if json_operacao:
                candlestick_patterns = json_operacao.get('Condições', {}).get('candlestick_patterns', None)
                padroes_candlestick = candlestick_patterns if candlestick_patterns else 'Não atendida'

                # Truncar o valor de 'bollinger_bands' se for maior que 20 caracteres
                bollinger_bands = json_operacao.get('Condições', {}).get('bollinger_bands', operacao['bollinger_bands'])[:20]

                # Executa a atualização
                cursor.execute("""
                    UPDATE operacoes
                    SET justificativa = %s, usuario = %s, tendencia = %s, macd = %s, bollinger_bands = %s,
                        volume = %s, padroes_candlestick = %s, ema_9 = %s
                    WHERE id_position = %s
                """, (
                    json_operacao.get('Justificativa', operacao['justificativa']),
                    json_operacao.get('Usuário', operacao['usuario']),
                    json_operacao.get('Condições', {}).get('tendencia', operacao['tendencia']),
                    json_operacao.get('Condições', {}).get('macd', operacao['macd']),
                    bollinger_bands,
                    json_operacao.get('Condições', {}).get('volume', operacao['volume']),
                    padroes_candlestick,
                    json_operacao.get('Condições', {}).get('ema_9', operacao['ema_9']),
                    operacao['id_position']
                ))
                conn.commit()
                print(f"Operação {operacao['id_position']} atualizada com dados do JSON.")

    except mysql.connector.Error as err:
        print(f"Erro ao atualizar operações: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

    # Atualizar operações no banco com os dados do JSON
    for operacao in operacoes_incompletas:
        json_operacao = buscar_dados_no_json_por_id(operacoes_json, operacao['id_position'])

        if json_operacao:
            candlestick_patterns = json_operacao.get('Condições', {}).get('candlestick_patterns', None)
            padroes_candlestick = candlestick_patterns if candlestick_patterns else 'Não atendida'

            # Truncar o valor de 'bollinger_bands' se for maior que 20 caracteres
            bollinger_bands = json_operacao.get('Condições', {}).get('bollinger_bands', operacao['bollinger_bands'])[:20]

            cursor.execute("""
                UPDATE operacoes
                SET justificativa = %s, usuario = %s, tendencia = %s, macd = %s, bollinger_bands = %s,
                    volume = %s, padroes_candlestick = %s, ema_9 = %s
                WHERE id_position = %s
            """, (
                json_operacao.get('Justificativa', operacao['justificativa']),
                json_operacao.get('Usuário', operacao['usuario']),
                json_operacao.get('Condições', {}).get('tendencia', operacao['tendencia']),
                json_operacao.get('Condições', {}).get('macd', operacao['macd']),
                bollinger_bands,
                json_operacao.get('Condições', {}).get('volume', operacao['volume']),
                padroes_candlestick,
                json_operacao.get('Condições', {}).get('ema_9', operacao['ema_9']),
                operacao['id_position']
            ))
            conn.commit()
            print(f"Operação {operacao['id_position']} atualizada com dados do JSON.")

    cursor.close()
    conn.close()

    # Atualizar operações no banco com os dados do JSON
    for operacao in operacoes_incompletas:
        json_operacao = buscar_dados_no_json_por_id(operacoes_json, operacao['id_position'])

        if json_operacao:
            candlestick_patterns = json_operacao.get('Condições', {}).get('candlestick_patterns', None)
            padroes_candlestick = candlestick_patterns if candlestick_patterns else 'Não atendida'

            cursor.execute("""
                UPDATE operacoes
                SET justificativa = %s, usuario = %s, tendencia = %s, macd = %s, bollinger_bands = %s,
                    volume = %s, padroes_candlestick = %s, ema_9 = %s
                WHERE id_position = %s
            """, (
                json_operacao.get('Justificativa', operacao['justificativa']),
                json_operacao.get('Usuário', operacao['usuario']),
                json_operacao.get('Condições', {}).get('tendencia', operacao['tendencia']),
                json_operacao.get('Condições', {}).get('macd', operacao['macd']),
                json_operacao.get('Condições', {}).get('bollinger_bands', operacao['bollinger_bands']),
                json_operacao.get('Condições', {}).get('volume', operacao['volume']),
                padroes_candlestick,
                json_operacao.get('Condições', {}).get('ema_9', operacao['ema_9']),
                operacao['id_position']
            ))
            conn.commit()
            print(f"Operação {operacao['id_position']} atualizada com dados do JSON.")

    cursor.close()
    conn.close()

def obter_preco_abertura(position_id):
    # Pega o histórico de negociações para a posição específica
    trades = mt5.history_deals_get(datetime.now() - timedelta(hours=24), datetime.now())
    
    if trades is None:
        print(f"Nenhuma negociação encontrada para a posição {position_id}.")
        return None

    # Procura a negociação de abertura (ORDER_TYPE_BUY ou ORDER_TYPE_SELL)
    for trade in trades:
        if trade.position_id == position_id:
            if trade.type in [mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_SELL]:
                return trade.price  # Retorna o preço de abertura
    
    return None  # Se não encontrar o preço de abertura

def carregar_dados_mt5_para_banco():
    if not mt5.initialize():
        print("Falha ao inicializar MetaTrader 5.")
        return
    
    # Pegar o histórico de negociações das últimas 24 horas
    deals = mt5.history_deals_get(datetime.now() - timedelta(hours=24), datetime.now())
    
    if deals is None:
        print("Nenhuma transação encontrada no histórico do MT5.")
        mt5.shutdown()
        return

    criar_tabela_operacoes()

    # Carregar os dados do JSON para capturar justificativa e usuário
    operacoes_json = carregar_dados_json()

    # Insere cada operação no banco apenas se tiver lucro/prejuízo e preço de fechamento
    for deal in deals:
        if deal.profit is not None and deal.profit != 0 and deal.price is not None:  # Verifica lucro/prejuízo e preço de fechamento
            
            tipo_operacao = mapear_tipo_operacao(deal, operacoes_json)[:20]
            
            # Obter o preço de abertura (price_open) com base no position_id
            preco_abertura = obter_preco_abertura(deal.position_id)
            
            # Verifica se conseguiu obter o preço de abertura
            if preco_abertura is None:
                print(f"Não foi possível obter o preço de abertura para a posição {deal.position_id}.")
                continue

            operacao = {
                'data_horario': datetime.fromtimestamp(deal.time),  # Converter timestamp para datetime
                'simbolo': deal.symbol,
                'tipo_operacao': tipo_operacao,
                'preco_abertura': preco_abertura,  # Preço de abertura obtido
                'preco_fechamento': deal.price,  # Preço de fechamento
                'lucro_prejuizo': deal.profit,   # Lucro ou prejuízo
                'id_position': deal.position_id,
                'justificativa': None,
                'usuario': None,
                'tendencia': 'N/A',
                'macd': 'N/A',
                'bollinger_bands': 'N/A',
                'volume': 'N/A',
                'padroes_candlestick': '',
                'ema_9': 'N/A'
            }

            # Buscar os dados do JSON (justificativa e usuário)
            if operacoes_json:
                json_operacao = buscar_dados_no_json_por_id(operacoes_json, deal.position_id)
                if json_operacao:
                    operacao['justificativa'] = json_operacao.get('Justificativa', None)
                    operacao['usuario'] = json_operacao.get('Usuário', None)

            # Inserir operação no banco de dados
            inserir_operacao_no_banco(operacao)

    mt5.shutdown()

def verificar_operacoes_passadas(condicoes_mercado_atual):
    conn = connect_to_db()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        return None

    cursor = conn.cursor(dictionary=True)

    # Consulta para encontrar operações com condições semelhantes no banco de dados
    sql = """
    SELECT * FROM operacoes
    WHERE tendencia = %s
      AND macd = %s
      AND bollinger_bands = %s
      AND volume = %s
      AND ema_9 = %s
    """

    valores = (
        condicoes_mercado_atual.get('tendencia', 'N/A'),
        condicoes_mercado_atual.get('macd', 'N/A'),
        condicoes_mercado_atual.get('bollinger_bands', 'N/A'),
        condicoes_mercado_atual.get('volume', 'N/A'),
        condicoes_mercado_atual.get('ema_9', 'N/A')
    )

    cursor.execute(sql, valores)
    operacoes_encontradas = cursor.fetchall()

    if not operacoes_encontradas:
        print("Nenhuma operação passada com as mesmas condições de mercado encontrada.")
        cursor.close()
        conn.close()
        return None

    # Ordenar as operações com lucro/prejuízo, considerando None como o menor valor
    operacoes_encontradas.sort(key=lambda op: op['lucro_prejuizo'] if op['lucro_prejuizo'] is not None else float('-inf'))

    # Selecionar a operação de maior prejuízo (primeira) e maior lucro (última)
    operacoes_selecionadas = [operacoes_encontradas[0], operacoes_encontradas[-1]] if len(operacoes_encontradas) > 1 else [operacoes_encontradas[0]]
    
    cursor.close()
    conn.close()
    
    return operacoes_selecionadas

if __name__ == "__main__":
    criar_tabela_operacoes()
    carregar_dados_mt5_para_banco()
    atualizar_operacao_com_dados_json()  