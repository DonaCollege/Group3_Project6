from pydantic import BaseModel

class VaRRequest(BaseModel):
    ticker: str
    confidence: float = 0.95
    simulations: int = 100_000
##
# @file analytics.py
# @brief Analytics-related endpoints.
#
# @details
# Provides CPU-intensive endpoints used for performance benchmarking.
# Includes volatility forecasting and heavy computational simulation.
##
