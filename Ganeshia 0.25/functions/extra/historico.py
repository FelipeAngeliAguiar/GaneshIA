from datetime import datetime

def log_trade(response_explanation, action_line):
    max_lines = 50
    log_file_path = 'trade_log.txt'

    try:
        with open(log_file_path, 'r') as log_file:
            lines = log_file.readlines()
    except FileNotFoundError:
        lines = []

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = (
        f"Horário: {timestamp}\n"
        f"Ação: {action_line}\n"
        f"Explicação: {response_explanation}\n"
        f"---------------------------------\n"
    )
    lines.append(log_entry)

    if len(lines) > max_lines:
        lines = lines[-max_lines:]

    with open(log_file_path, 'w') as log_file:
        log_file.writelines(lines)
