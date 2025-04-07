def read_trade_log():
    try:
        with open('trade_log.txt', 'r') as log_file:
            return log_file.read()
    except FileNotFoundError:
        return "O log de trade não foi encontrado."