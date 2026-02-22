# import math

# def run_cpu_heavy_analysis(iterations: int):
#     total = 0
#     for i in range(iterations):
#         total += math.sqrt(i)
#     return total

# def compute_volatility(ticker: str, period: str, iterations: int):
#     """
#     TODO (Nikhil):
#     - Replace loop with DB aggregation
#     - Optimize query
#     """
#     acc = 0
#     for i in range(iterations):
#         acc += (i % 10) * 0.01
#     return {
#         "ticker": ticker,
#         "period": period,
#         "forecasted_volatility": round(acc / iterations, 4),
#         "risk_level": "High" if acc / iterations > 0.3 else "Low"
#     }

##
# @file risk.py
# @brief Risk analysis endpoints.
#
# @details
# Provides Value at Risk (VaR) calculation using Monte Carlo simulation.
# Designed to simulate computational load for performance evaluation.
##
from data.database import Database
import statistics

db = Database()

def run_cpu_heavy_analysis(window: int):
    # Use real data instead of dummy loop
    all_stocks = db.get_all_stocks(1000)
    closes = [row[6] for row in all_stocks[-window:]]  # Last N closes
    if len(closes) < 2:
        return {"error": "Not enough data"}
    return {
        "mean_close": statistics.mean(closes),
        "std_dev": statistics.stdev(closes) if len(closes) > 1 else 0
    }

def compute_volatility(ticker: str, period: str, iterations: int):
    rows = db.get_stocks_by_company(ticker, 252)  # ~1y trading days
    closes = [row[6] for row in rows]
    if len(closes) < 2:
        return {"error": "No data for ticker"}
    
    # Real volatility (std dev of returns)
    returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
    vol = statistics.stdev(returns) * (252 ** 0.5)  # Annualized
    
    return {
        "ticker": ticker,
        "period": period,
        "forecasted_volatility": round(vol, 4),
        "risk_level": "High" if vol > 0.3 else "Low",
        "data_points": len(closes)
    }
