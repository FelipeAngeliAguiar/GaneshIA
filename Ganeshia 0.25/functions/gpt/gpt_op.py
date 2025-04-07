import openai
import MetaTrader5 as mt5 

def get_close_or_reassess_signal(prompt, symbol):
    from functions.extract import extract_close_or_reassess_action
    from functions.extra import close_position
    
    try:
        full_prompt = f"{prompt}"
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um analista de mercado. Forneça respostas objetivas e concisas, sem explicações longas."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=100
        )
        content = response.choices[0].message['content'].strip()

        # Extract the action (fechar or manter)
        action_line = extract_close_or_reassess_action(content)
        print(f"Action line received: {action_line}")
        print(f"GPT response explanation: {content}")  # Log response for debugging

        if "fechar" in action_line.lower():
            # Fetch the open position for the symbol
            positions = mt5.positions_get(symbol=symbol)
            if positions:
                position = positions[0]  # Assuming there's only one open position for the symbol
                reason = f"Recomendação GPT: {content}"
                close_position(position, reason)  # Pass the position object, not just the symbol
                print(f"Operação para o símbolo {symbol} foi fechada conforme recomendado pelo GPT.")
            else:
                print(f"Nenhuma posição aberta encontrada para o símbolo {symbol}.")
        elif "manter" in action_line.lower():
            print(f"A operação para o símbolo {symbol} foi mantida conforme recomendado pelo GPT.")
        else:
            print(f"Comando não reconhecido: {action_line}")
        
        return content, action_line
    except Exception as e:
        print(f"Error fetching close/reassess signal: {e}")
        return None, (None, None)
