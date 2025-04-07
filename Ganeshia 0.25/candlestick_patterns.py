def identify_candlestick_patterns(data):
    patterns = []

    if len(data) >= 2:
        # Bullish Engulfing
        if data['close'].iloc[-1] > data['open'].iloc[-1] and data['close'].iloc[-2] < data['open'].iloc[-2] and data['close'].iloc[-1] > data['open'].iloc[-2] and data['open'].iloc[-1] < data['close'].iloc[-2]:
            patterns.append("Bullish Engulfing")

        # Bearish Engulfing
        if data['close'].iloc[-1] < data['open'].iloc[-1] and data['close'].iloc[-2] > data['open'].iloc[-2] and data['close'].iloc[-1] < data['open'].iloc[-2] and data['open'].iloc[-1] > data['close'].iloc[-2]:
            patterns.append("Bearish Engulfing")

        # Hammer
        if data['close'].iloc[-1] > data['open'].iloc[-1] and (data['high'].iloc[-1] - data['low'].iloc[-1]) > 2 * (data['open'].iloc[-1] - data['close'].iloc[-1]) and (data['close'].iloc[-1] - data['low'].iloc[-1]) / (.001 + data['high'].iloc[-1] - data['low'].iloc[-1]) > 0.6:
            patterns.append("Hammer")

        # Inverted Hammer
        if data['close'].iloc[-1] > data['open'].iloc[-1] and (data['high'].iloc[-1] - data['low'].iloc[-1]) > 2 * (data['close'].iloc[-1] - data['open'].iloc[-1]) and (data['high'].iloc[-1] - data['close'].iloc[-1]) / (.001 + data['high'].iloc[-1] - data['low'].iloc[-1]) > 0.6:
            patterns.append("Inverted Hammer")

        # Shooting Star
        if data['close'].iloc[-1] < data['open'].iloc[-1] and (data['high'].iloc[-1] - data['low'].iloc[-1]) > 2 * (data['close'].iloc[-1] - data['open'].iloc[-1]) and (data['high'].iloc[-1] - data['close'].iloc[-1]) / (.001 + data['high'].iloc[-1] - data['low'].iloc[-1]) > 0.6:
            patterns.append("Shooting Star")

        # Doji
        if abs(data['close'].iloc[-1] - data['open'].iloc[-1]) <= (data['high'].iloc[-1] - data['low'].iloc[-1]) * 0.1:
            patterns.append("Doji")

        # Hanging Man
        if data['close'].iloc[-1] < data['open'].iloc[-1] and (data['high'].iloc[-1] - data['low'].iloc[-1]) > 2 * (data['open'].iloc[-1] - data['close'].iloc[-1]) and (data['close'].iloc[-1] - data['low'].iloc[-1]) / (.001 + data['high'].iloc[-1] - data['low'].iloc[-1]) > 0.6:
            patterns.append("Hanging Man")

        # Harami (Bullish)
        if data['close'].iloc[-2] < data['open'].iloc[-2] and data['close'].iloc[-1] > data['open'].iloc[-1] and data['close'].iloc[-1] <= data['open'].iloc[-2] and data['open'].iloc[-1] >= data['close'].iloc[-2]:
            patterns.append("Bullish Harami")

        # Harami (Bearish)
        if data['close'].iloc[-2] > data['open'].iloc[-2] and data['close'].iloc[-1] < data['open'].iloc[-1] and data['close'].iloc[-1] >= data['open'].iloc[-2] and data['open'].iloc[-1] <= data['close'].iloc[-2]:
            patterns.append("Bearish Harami")
            
        if data['open'].iloc[-1] == data['close'].iloc[-1] and (data['high'].iloc[-1] - data['close'].iloc[-1]) < 0.1 * (data['high'].iloc[-1] - data['low'].iloc[-1]):
            patterns.append("Dragonfly Doji")

        # Gravestone Doji (Indica reversão de alta para baixa)
        if data['open'].iloc[-1] == data['close'].iloc[-1] and (data['close'].iloc[-1] - data['low'].iloc[-1]) < 0.1 * (data['high'].iloc[-1] - data['low'].iloc[-1]):
            patterns.append("Gravestone Doji")

        # Belt Hold (Alta)
        if data['close'].iloc[-1] > data['open'].iloc[-1] and (data['low'].iloc[-1] == data['open'].iloc[-1]) and (data['close'].iloc[-1] - data['open'].iloc[-1]) > (data['high'].iloc[-1] - data['close'].iloc[-1]):
            patterns.append("Bullish Belt Hold")

        # Belt Hold (Baixa)
        if data['close'].iloc[-1] < data['open'].iloc[-1] and (data['high'].iloc[-1] == data['open'].iloc[-1]) and (data['open'].iloc[-1] - data['close'].iloc[-1]) > (data['close'].iloc[-1] - data['low'].iloc[-1]):
            patterns.append("Bearish Belt Hold")

    if len(data) >= 3:
        # Morning Star
        if data['close'].iloc[-3] < data['open'].iloc[-3] and abs(data['close'].iloc[-2] - data['open'].iloc[-2]) < (data['high'].iloc[-2] - data['low'].iloc[-2]) * 0.1 and data['close'].iloc[-1] > data['open'].iloc[-1] and data['close'].iloc[-1] > data['close'].iloc[-3]:
            patterns.append("Morning Star")

        # Evening Star
        if data['close'].iloc[-3] > data['open'].iloc[-3] and abs(data['close'].iloc[-2] - data['open'].iloc[-2]) < (data['high'].iloc[-2] - data['low'].iloc[-2]) * 0.1 and data['close'].iloc[-1] < data['open'].iloc[-1] and data['close'].iloc[-1] < data['close'].iloc[-3]:
            patterns.append("Evening Star")

        # Three White Soldiers
        if all(data['close'].iloc[-i] > data['open'].iloc[-i] for i in range(1, 4)) and all(data['close'].iloc[-i] > data['close'].iloc[-i-1] for i in range(1, 3)):
            patterns.append("Three White Soldiers")

        # Three Black Crows
        if all(data['close'].iloc[-i] < data['open'].iloc[-i] for i in range(1, 3)) and all(data['close'].iloc[-i] < data['close'].iloc[-i-1] for i in range(1, 3)):
            patterns.append("Three Black Crows")

        # Dark Cloud Cover
        if data['close'].iloc[-2] > data['open'].iloc[-2] and data['close'].iloc[-1] < data['open'].iloc[-1] and data['close'].iloc[-1] > data['open'].iloc[-2] and data['close'].iloc[-1] < 0.5 * (data['close'].iloc[-2] - data['open'].iloc[-2]):
            patterns.append("Dark Cloud Cover")

        # Piercing Line
        if data['close'].iloc[-2] < data['open'].iloc[-2] and data['close'].iloc[-1] > data['open'].iloc[-1] and data['close'].iloc[-1] < data['open'].iloc[-2] and data['close'].iloc[-1] > 0.5 * (data['open'].iloc[-2] - data['close'].iloc[-2]):
            patterns.append("Piercing Line")

        # Three Inside Up
        if data['close'].iloc[-3] < data['open'].iloc[-3] and data['close'].iloc[-2] > data['open'].iloc[-2] and data['close'].iloc[-2] <= data['open'].iloc[-3] and data['open'].iloc[-2] >= data['close'].iloc[-3] and data['close'].iloc[-1] > data['open'].iloc[-1]:
            patterns.append("Three Inside Up")

        # Three Inside Down
        if data['close'].iloc[-3] > data['open'].iloc[-3] and data['close'].iloc[-2] < data['open'].iloc[-2] and data['close'].iloc[-2] >= data['open'].iloc[-3] and data['open'].iloc[-2] <= data['close'].iloc[-3] and data['close'].iloc[-1] < data['open'].iloc[-1]:
            patterns.append("Three Inside Down")

        # Tweezer Bottom
        if data['low'].iloc[-1] == data['low'].iloc[-2] and data['close'].iloc[-1] > data['open'].iloc[-1] and data['close'].iloc[-2] < data['open'].iloc[-2]:
            patterns.append("Tweezer Bottom")

        # Tweezer Top
        if data['high'].iloc[-1] == data['high'].iloc[-2] and data['close'].iloc[-1] < data['open'].iloc[-1] and data['close'].iloc[-2] > data['open'].iloc[-2]:
            patterns.append("Tweezer Top")
            
        # Rising Three Methods
        if data['close'].iloc[-3] > data['open'].iloc[-3] and all(data['close'].iloc[-i] < data['open'].iloc[-i] for i in range(2, 4)) and data['close'].iloc[-1] > data['open'].iloc[-1] and data['close'].iloc[-1] > data['close'].iloc[-3]:
            patterns.append("Rising Three Methods")

        # Falling Three Methods
        if data['close'].iloc[-3] < data['open'].iloc[-3] and all(data['close'].iloc[-i] > data['open'].iloc[-i] for i in range(2, 4)) and data['close'].iloc[-1] < data['open'].iloc[-1] and data['close'].iloc[-1] < data['close'].iloc[-3]:
            patterns.append("Falling Three Methods")

        # Abandoned Baby
        if abs(data['open'].iloc[-2] - data['close'].iloc[-2]) <= (data['high'].iloc[-2] - data['low'].iloc[-2]) * 0.1 and (data['low'].iloc[-1] > data['high'].iloc[-2] or data['high'].iloc[-1] < data['low'].iloc[-2]):
            if data['close'].iloc[-3] < data['open'].iloc[-3] and data['close'].iloc[-1] > data['open'].iloc[-1]:
                patterns.append("Bullish Abandoned Baby")
            elif data['close'].iloc[-3] > data['open'].iloc[-3] and data['close'].iloc[-1] < data['open'].iloc[-1]:
                patterns.append("Bearish Abandoned Baby")

    return patterns
