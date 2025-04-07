def calculate_fibonacci_retracement(high, low):
    diff = high - low
    levels = {
        'level_0': high,
        'level_23.6': high - 0.236 * diff,
        'level_38.2': high - 0.382 * diff,
        'level_50': high - 0.5 * diff,
        'level_61.8': high - 0.618 * diff,
        'level_100': low,
    }
    return levels