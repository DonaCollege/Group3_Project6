import math

def run_cpu_heavy_analysis(iterations: int):
    total = 0
    for i in range(iterations):
        total += math.sqrt(i)
    return total

def compute_volatility(ticker: str, period: str, iterations: int):
    """
    TODO (Nikhil):
    - Replace loop with DB aggregation
    - Optimize query
    """
    acc = 0
    for i in range(iterations):
        acc += (i % 10) * 0.01
    return {
        "ticker": ticker,
        "period": period,
        "forecasted_volatility": round(acc / iterations, 4),
        "risk_level": "High" if acc / iterations > 0.3 else "Low"
    }
