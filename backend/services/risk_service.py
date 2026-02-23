# import random
# from schemas.risk import VaRRequest

# def calculate_var(request: VaRRequest):
#     """
#     TODO (Nikhil):
#     - Replace random simulation with DB-based returns
#     """
#     simulated_losses = [
#         random.gauss(0, 1) for _ in range(request.simulations)
#     ]
#     simulated_losses.sort()
#     index = int((1 - request.confidence) * len(simulated_losses))
#     return {
#         "ticker": request.ticker,
#         "confidence": request.confidence,
#         "value_at_risk": round(simulated_losses[index], 4)
#     }

##
# @file analytics_service.py
# @brief Business logic for analytics computations.
#
# @details
# Contains CPU-heavy functions used to simulate analytical workloads
# for performance and stress testing experiments.
##
from data.database import Database
import numpy as np
from schemas.risk import VaRRequest

db = Database()

def calculate_var(request: VaRRequest):
    rows = db.get_stocks_by_company(request.ticker, 252)
    closes = [row[6] for row in rows]
    if len(closes) < 10:
        return {"error": "Insufficient data"}
    
    returns = np.diff(np.log(closes))  # Log returns
    var = np.percentile(returns, (1 - request.confidence) * 100)
    
    return {
        "ticker": request.ticker,
        "confidence": request.confidence,
        "value_at_risk": round(var, 4),
        "data_points": len(returns)
    }
